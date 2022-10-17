import asyncio
from common import *
from time import sleep, time
from execution_plan_util import locate_operation

GRAPH_ID = "index_create"
redis_graph = None
redis_con = None

class testIndexCreationFlow():
    def __init__(self):
        self.env = Env(decodeResponses=True)
        global redis_graph
        global redis_con
        redis_con = self.env.getConnection()
        redis_graph = Graph(redis_con, GRAPH_ID)

    def index_under_construction(self, g):
        # validate index is being populated
        res = g.query("CALL db.indexes() yield status")
        return "UNDER CONSTRUCTION" in res.result_set[0][0]

    # full-text index creation
    def test01_fulltext_index_creation(self):
        # create an index over L:v0
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex('L', 'v0')")
        self.env.assertEquals(result.indices_created, 1)

        # create an index over L:v1
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex('L', 'v1')")
        self.env.assertEquals(result.indices_created, 1)

        # create an index over L:v1 and L:v2
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex('L', 'v1', 'v2')")
        self.env.assertEquals(result.indices_created, 1)

        # create an index over L:v0, L:v1 and L:v2
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex('L', 'v0', 'v1', 'v2')")
        self.env.assertEquals(result.indices_created, 0)

        # create an index over L:v2, L:v1 and L:v0
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex('L', 'v2', 'v1', 'v0')")
        self.env.assertEquals(result.indices_created, 0)

        # create an index over L:v3 and L:v4
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex('L', 'v3', 'v4')")
        self.env.assertEquals(result.indices_created, 2)

        # create an index over L:v5 and L:v6
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L' }, 'v5', 'v6')")
        self.env.assertEquals(result.indices_created, 2)

    def test02_fulltext_index_creation_label_config(self):
        # create an index over L1:v1
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L1' }, 'v1')")
        self.env.assertEquals(result.indices_created, 1)

        # create an index over L1:v2, v3
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L1' }, 'v2', 'v3')")
        self.env.assertEquals(result.indices_created, 2)

        # create an index over L2:v1 with stopwords
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L2', stopwords: ['The'] }, 'v1')")
        self.env.assertEquals(result.indices_created, 1)

        # create an index over L2:v2
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L2' }, 'v2')")
        self.env.assertEquals(result.indices_created, 1)

        try:
            # try to create an index, without specifying the label
            result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ stopwords: ['The'] }, 'v4')")
            assert(False)
        except ResponseError as e:
            self.env.assertIn("Label is missing", str(e))

        try:
            # create an index over L1:v4 with stopwords should failed
            result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L1', stopwords: ['The'] }, 'v4')")
            assert(False)
        except ResponseError as e:
            self.env.assertIn("Index already exists configuration can't be changed", str(e))

        try:
            # create an index over L1:v4 with language should failed
            result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L1', language: 'english' }, 'v4')")
            assert(False)
        except ResponseError as e:
            self.env.assertIn("Index already exists configuration can't be changed", str(e))

        # drop L1 index
        result = redis_graph.query("CALL db.idx.fulltext.drop('L1')")
        self.env.assertEquals(result.indices_deleted, 1)

        try:
            # create an index over L1:v4 with an unsupported language, expecting to failed
            result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L1', language: 'x' }, 'v4')")
            assert(False)
        except ResponseError as e:
            self.env.assertIn("Language is not supported", str(e))

        # create an index over L1:v4 with language
        result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L1', language: 'english' }, 'v4')")
        self.env.assertEquals(result.indices_created, 1)

        try:
            # create an index over L3:v1 with stopwords should failed
            # stopwords must be provided as an array of strings
            result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L3', stopwords: 'The' }, 'v1')")
            assert(False)
        except ResponseError as e:
            self.env.assertIn("Stopwords must be array", str(e))

        try:
            # create an index over L3:v1 with language should failed
            # language must be provided as a string
            result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex({ label: 'L3', language: ['english'] }, 'v1')")
            assert(False)
        except ResponseError as e:
            self.env.assertIn("Language must be string", str(e))

        try:
            # create an index over L3 should failed, missing field(s)
            result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex('L3', { })")
            assert(False)
        except ResponseError as e:
            self.env.assertIn("Field is missing", str(e))

        try:
            # create an index over L3:v1 with weight of type string should failed
            # weight must be provided as numeric
            result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex('L3', { field: 'v1', weight: '1' })")
            assert(False)
        except ResponseError as e:
            self.env.assertIn("Weight must be numeric", str(e))

        try:
            # create an index over L3:v1 with nostem of type string should failed
            # nostem must be boolean
            result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex('L3', { field: 'v1', nostem: 'true' })")
            assert(False)
        except ResponseError as e:
            self.env.assertIn("Nostem must be bool", str(e))
        
        try:
            # create an index over L3:v1 with phonetic of type bool should failed
            # phonetic must be a string
            result = redis_graph.query("CALL db.idx.fulltext.createNodeIndex('L3', { field: 'v1', phonetic: true })")
            assert(False)
        except ResponseError as e:
            self.env.assertIn("Phonetic must be a string", str(e))

    def test03_multi_prop_index_creation(self):
        # create an index over person:age and person:name
        result = redis_graph.query("CREATE INDEX ON :person(age, name)")
        self.env.assertEquals(result.indices_created, 2)

        # try to create an index over person:age and person:name, index shouldn't be created as it already exist
        result = redis_graph.query("CREATE INDEX ON :person(age, name)")
        self.env.assertEquals(result.indices_created, 0)

        # try to create an index over person:name and person:age, index shouldn't be created as it already exist
        result = redis_graph.query("CREATE INDEX ON :person(name, age)")
        self.env.assertEquals(result.indices_created, 0)

        # try to create an index over person:age and person:name and person:height, index for height should be created as the rest already exist
        result = redis_graph.query("CREATE INDEX ON :person(age, age, name, height)")
        self.env.assertEquals(result.indices_created, 1)

        # try to create an index over person:gender and person:name and person:height, index for gender should be created as the rest already exist
        result = redis_graph.query("CREATE INDEX ON :person(gender, gender, name, height)")
        self.env.assertEquals(result.indices_created, 1)

    def test04_index_creation_pattern_syntax(self):
        # create an index over user:age and user:name
        result = redis_graph.query("CREATE INDEX FOR (p:user) ON (p.age, p.name)")
        self.env.assertEquals(result.indices_created, 2)

        # create an index over follow:prop1 and follow:prop2
        result = redis_graph.query("CREATE INDEX FOR ()-[r:follow]-() ON (r.prop1, r.prop2)")
        self.env.assertEquals(result.indices_created, 2)

    def test05_index_delete(self):
        def _create_drop_index(graph_id):
            env = Env(decodeResponses=True)
            redis_con = env.getConnection()
            for _ in range(1, 100):
                redis_con.execute_command("GRAPH.QUERY", graph_id, "CREATE (a:L), (n:L), (n)-[:T]->(a)")
                redis_con.execute_command("GRAPH.QUERY", graph_id, "CREATE INDEX FOR ()-[n:T]-() ON (n.p)")
                redis_con.execute_command("GRAPH.DELETE", graph_id)

        if "to_thread" not in dir(asyncio):
            _create_drop_index(1)
        else:
            loop = asyncio.get_event_loop()
            tasks = []
            for i in range(1, 20):
                tasks.append(loop.create_task(asyncio.to_thread(_create_drop_index, i)))

            loop.run_until_complete(asyncio.wait(tasks))

    def test06_async_index_creation(self):
        # 1. create a large graph
        # 2. create an index
        # 3. while the index is being constructed make sure:
        # 3.a. we're able to write to the graph
        # 3.b. we're able to read
        # 3.c. queries aren't utilizing the index while it is being constructed

        min_node_v = 0
        max_node_v = 1500000

        g = Graph(self.env.getConnection(), "async-index")

        #-----------------------------------------------------------------------
        # create a large graph
        #-----------------------------------------------------------------------

        q = "UNWIND range($min_v, $max_v) AS x CREATE (:L {v:x})"
        g.query(q, {'min_v': min_node_v, 'max_v': max_node_v})

        #-----------------------------------------------------------------------
        # create an index
        #-----------------------------------------------------------------------

        q = "CREATE INDEX FOR (n:L) on (n.v)"
        res = g.query(q)
        self.env.assertEquals(res.indices_created, 1)

        #-----------------------------------------------------------------------
        # validate index is being populated
        #-----------------------------------------------------------------------

        self.env.assertTrue(self.index_under_construction(g))

        # while the index is being constructed
        # perform CRUD operations

        #-----------------------------------------------------------------------
        # read while index is being constructed
        #-----------------------------------------------------------------------

        q = "MATCH (n:L) WHERE n.v = 41 RETURN n.v LIMIT 1"
        res = g.query(q)
        #self.evn.assertEquals(res.result_set[0][0], 41)

        plan = g.explain(q)
        self.env.assertIsNone(locate_operation(plan.structured_plan, "Node By Index Scan"))

        #-----------------------------------------------------------------------
        # write while index is being constructed
        #-----------------------------------------------------------------------
    
        # create a new node
        q = "CREATE (:L {v:$v})"
        g.query(q, {'v': max_node_v + 10})

        # update a node which had yet to be indexed
        q = "MATCH (n:L) WHERE ID(n) = $id WITH n LIMIT 1 SET n.v = $new_v"
        g.query(q, {'id': max_node_v - 10, 'new_v': -max_node_v})

        # update a node which is already indexed
        g.query(q, {'id': 1, 'new_v': -1})

        # delete a node which had yet to be indexed
        q = "MATCH (n:L) WHERE ID(n) = $id WITH n LIMIT 1 DELETE n"
        g.query(q, {'id': max_node_v - 9})

        # delete an indexed node
        q = "MATCH (n:L) WHERE ID(n) = $id WITH n LIMIT 1 DELETE n"
        g.query(q, {'id': 2})

        #-----------------------------------------------------------------------
        # validate index is being populated
        #-----------------------------------------------------------------------

        self.env.assertTrue(self.index_under_construction(g))

        # wait for index to become operational
        while self.index_under_construction(g):
            sleep(0.5) # sleep for .5 seconds

        # index should be operational
        self.env.assertFalse(self.index_under_construction(g))

    def test07_delete_interrupt_async_index_creation(self):
        # 1. create a large graph
        # 2. create an index
        # 3. delete the graph while the index is being constructed

        key = "async-index"
        min_node_v = 0
        max_node_v = 1500000
        conn = self.env.getConnection()

        # clear DB
        conn.flushall()

        g = Graph(self.env.getConnection(), key)

        #-----------------------------------------------------------------------
        # create a large graph
        #-----------------------------------------------------------------------

        q = "UNWIND range($min_v, $max_v) AS x CREATE (:L {v:x})"
        g.query(q, {'min_v': min_node_v, 'max_v': max_node_v})

        #-----------------------------------------------------------------------
        # create an index
        #-----------------------------------------------------------------------

        q = "CREATE INDEX FOR (n:L) on (n.v)"
        res = g.query(q)
        self.env.assertEquals(res.indices_created, 1)

        #-----------------------------------------------------------------------
        # validate index is being populated
        #-----------------------------------------------------------------------

        self.env.assertTrue(self.index_under_construction(g))

        #-----------------------------------------------------------------------
        # delete graph while the index is being constructed 
        #-----------------------------------------------------------------------

        conn.delete(key)

        # graph key should be removed, index creation should run to completion
        self.env.assertFalse(conn.exists(key))

        # at the moment there's no way of checking index status once its graph
        # key had been removed

    def test08_multi_index_creation(self):
        # interrupt index creation by adding/removing fields
        #
        # 1. create a large graph
        # 2. create an index
        # 3. modify the index while it is being populated

        key = "async-index"
        min_node_v = 0
        max_node_v = 1500000
        conn = self.env.getConnection()

        # clear DB
        conn.flushall()

        g = Graph(self.env.getConnection(), key)

        #-----------------------------------------------------------------------
        # create a large graph
        #-----------------------------------------------------------------------

        q = "UNWIND range($min_v, $max_v) AS x CREATE (:L {v:x, a:x, b:x})"
        g.query(q, {'min_v': min_node_v, 'max_v': max_node_v})

        #-----------------------------------------------------------------------
        # create an index
        #-----------------------------------------------------------------------

        # determine how much time does it take to construct our index
        start = time()

        q = "CREATE INDEX FOR (n:L) on (n.v)"
        res = g.query(q)
        self.env.assertEquals(res.indices_created, 1)

        # wait for index to become operational
        while self.index_under_construction(g):
            sleep(0.5) # sleep for .5 seconds

        # total index creation time
        elapsed = time() - start

        #-----------------------------------------------------------------------
        # drop the index
        #-----------------------------------------------------------------------

        q = "DROP INDEX ON :L(v)"
        res = g.query(q)
        self.env.assertEquals(res.indices_deleted, 1)

        # recreate the index, but this time introduce additionl fields
        # while the index is being populated

        start = time()

        # introduce a new field
        q = "CREATE INDEX FOR (n:L) on (n.a)"
        res = g.query(q)
        self.env.assertEquals(res.indices_created, 1)

        # introduce a new field
        q = "CREATE INDEX FOR (n:L) on (n.b)"
        res = g.query(q)
        self.env.assertEquals(res.indices_created, 1)

        # remove field
        q = "DROP INDEX ON :L(a)"
        res = g.query(q)
        self.env.assertEquals(res.indices_deleted, 1)

        # introduce a new field
        q = "CREATE INDEX FOR (n:L) on (n.v)"
        res = g.query(q)
        self.env.assertEquals(res.indices_created, 1)

        # wait for index to become operational
        while self.index_under_construction(g):
            sleep(0.5) # sleep for .5 seconds

        elapsed_2 = time() - start

        # although we've constructed a larger index
        # new index includes 2 fields (b,v) while the former index included just
        # one (v) we're expecting thier overall construction time to be similar
        self.env.assertTrue(elapsed_2 < elapsed * 1.2)

