from collections import Counter
from RLTest import Env

from redis.commands.graph import Graph
from redis.commands.graph.node import Node
from redis.commands.graph.edge import Edge
from redis.commands.graph.path import Path

def nodeToString(value):
    res = '('
    if value.alias:
        res += value.alias
    if value.labels:
        res += ':' + ":".join(value.labels)
    if value.properties:
        props = ', '.join(key+': '+toString(val)
                          for key, val in value.properties.items())
        if value.labels:
            res += " "
        res += '{' + props + '}'
    res += ')'
    value = res
    return value

def edgeToString(value):
    res = "["
    if value.relation:
        res += ":" + value.relation
    if value.properties:
        props = ', '.join(key+': '+toString(val)
                          for key, val in value.properties.items())
        if value.relation:
            res += " "
        res += '{' + props + '}'
    res += ']'
    value = res
    return value

def listToString(listToConvert):
    strValue = '['
    strValue += ", ".join(map(lambda value: toString(value), listToConvert))
    strValue += ']'
    return strValue

def pathToString(pathToConvert):
    strValue = "<"
    nodes_count = pathToConvert.nodes_count()
    for i in range(0, nodes_count - 1):
        node = pathToConvert.get_node(i)
        node_str = nodeToString(node)
        edge = pathToConvert.get_relationship(i)
        edge_str = edgeToString(edge)
        strValue += node_str + "-" + edge_str + "->" if edge.src_node == node.id else node_str + "<-" + edge_str + "-"

    strValue += nodeToString(pathToConvert.get_node(nodes_count - 1)) if nodes_count > 0 else ""
    strValue += ">"
    return strValue

def dictToString(dictToConvert):
    size = len(dictToConvert)
    strValue = '{'
    for idx, item in enumerate(dictToConvert.items()):
        strValue += item[0] + ": "
        strValue += toString(item[1])
        if idx < size - 1:
            strValue += ", "
    strValue += '}'
    return strValue

def toString(value):
    if isinstance(value, bool):
        if value is True:
            return "true"
        elif value is False:
            return "false"
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        float_str = str(value)
        float_str = float_str.replace("e+", "e")
        return float_str
    elif isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, Node):
        return nodeToString(value)
    elif isinstance(value, Edge):
        return edgeToString(value)
    elif isinstance(value, list):
        return listToString(value)
    elif isinstance(value, Path):
        return pathToString(value)
    elif isinstance(value, dict):
        return dictToString(value)
    elif value == None:
        return "null"

def prepare_actual_row(row):
    return tuple(toString(cell) for cell in row)

def prepare_expected_row(row):
    return tuple(cell for cell in row)

def assert_empty_resultset(resultset):
    Env.RTestInstance.currEnv.assertEquals(len(resultset.result_set), 0)

# check value of a designated statistic
def assert_statistics(resultset, stat, value):
    if stat == "+nodes":
        Env.RTestInstance.currEnv.assertEquals(resultset.nodes_created, value)
    elif stat == "+relationships":
        Env.RTestInstance.currEnv.assertEquals(resultset.relationships_created, value)
    elif stat == "-relationships":
        Env.RTestInstance.currEnv.assertEquals(resultset.relationships_deleted, value)
    elif stat == "+labels":
        Env.RTestInstance.currEnv.assertEquals(resultset.labels_added, value)
    elif stat == "-labels":
        Env.RTestInstance.currEnv.assertEquals(resultset.labels_removed, value)
    elif stat == "+properties":
        Env.RTestInstance.currEnv.assertEquals(resultset.properties_set, value)
    elif stat == "-properties":
        Env.RTestInstance.currEnv.assertEquals(resultset.properties_removed, value)
    elif stat == "-nodes":
        Env.RTestInstance.currEnv.assertEquals(resultset.nodes_deleted, value)
    else:
        print(stat)
        Env.RTestInstance.currEnv.assertTrue(False)

# checks resultset statistics for no graph modifications
def assert_no_modifications(resultset):
    Env.RTestInstance.currEnv.assertEquals(sum([resultset.nodes_created, resultset.nodes_deleted,
                resultset.properties_set, resultset.relationships_created,
                resultset.relationships_deleted]), 0)

def assert_resultset_length(resultset, length):
    Env.RTestInstance.currEnv.assertEquals(len(resultset.result_set), length)

def assert_resultsets_equals_in_order(actual, expected):
    rowCount = len(expected.rows)
    # check amount of rows
    assert_resultset_length(actual, rowCount)
    for rowIdx in range(rowCount):
        actualRow = prepare_actual_row(actual.result_set[rowIdx])
        expectedRow = prepare_expected_row(expected.rows[rowIdx])
        # compare rows
        Env.RTestInstance.currEnv.assertEquals(actualRow, expectedRow)

def assert_resultsets_equals(actual, expected):
    # Convert each row to a tuple, and maintain a count of how many times that row appears
    actualCtr = Counter(prepare_actual_row(row) for row in actual.result_set)
    expectedCtr = Counter(prepare_expected_row(row) for row in expected)
    # Validate that the constructed Counters are equal
    Env.RTestInstance.currEnv.assertEquals(actualCtr, expectedCtr)