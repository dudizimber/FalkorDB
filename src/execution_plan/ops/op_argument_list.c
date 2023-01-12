/*
 * Copyright Redis Ltd. 2018 - present
 * Licensed under your choice of the Redis Source Available License 2.0 (RSALv2) or
 * the Server Side Public License v1 (SSPLv1).
 */

#include "op.h"
#include "RG.h"
#include "op_argument_list.h"

// Forward declarations
static Record ArgumentListConsume(OpBase *opBase);
static OpResult ArgumentListReset(OpBase *opBase);
static OpBase *ArgumentListClone(const ExecutionPlan *plan, const OpBase *opBase);
static void ArgumentListFree(OpBase *opBase);

OpBase *NewArgumentListOp
(
	const ExecutionPlan *plan,  // plan to bind the operation to
	const char **variables     // bound variables
) {
	ArgumentList *op = rm_malloc(sizeof(ArgumentList));
	op->record_list = NULL;

	// Set our Op operations
	OpBase_Init((OpBase *)op, OPType_ARGUMENT_LIST, "Argument List", NULL,
				ArgumentListConsume, ArgumentListReset, NULL, ArgumentListClone, ArgumentListFree, false, plan);

	uint variable_count = array_len(variables);
	for(uint i = 0; i < variable_count; i ++) {
		OpBase_Modifies((OpBase *)op, variables[i]);
	}

	return (OpBase *)op;
}

static Record ArgumentListConsume(OpBase *opBase) {
	ArgumentList *arg = (ArgumentList *)opBase;

	if(arg->record_list) {
		if(array_len(arg->record_list) > 0) {
			return array_pop(arg->record_list);
		}
	}
    // if the list is empty - return NULL (depleted)
    return NULL;
}

static OpResult ArgumentListReset(OpBase *opBase) {
	// Reset operation, freeing the Record if one is held.
	ArgumentList *arg = (ArgumentList *)opBase;

	return OP_OK;
}

void ArgumentList_AddRecordList(ArgumentList *arg, Record *record_list) {
	ASSERT(!arg->record_list && "tried to insert into a populated Argument op");
	arg->record_list = record_list;
}

static inline OpBase *ArgumentListClone(const ExecutionPlan *plan, const OpBase *opBase) {
	ASSERT(opBase->type == OPType_ARGUMENT_LIST);
	return NewArgumentListOp(plan, opBase->modifies);
}

static void ArgumentListFree(OpBase *opBase) {
	ArgumentList *arg = (ArgumentList *)opBase;
	// if(arg->r) {
	// 	OpBase_DeleteRecord(arg->r);
	// 	arg->r = NULL;
	// }
}

