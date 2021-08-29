/*
 * Copyright 2018-2021 Redis Labs Ltd. and Contributors
 *
 * This file is available under the Redis Labs Source Available License Agreement
 */

#pragma once

#include "op.h"
#include "op_argument.h"
#include "../runtime_execution_plan.h"
#include "../../../ops/op_apply.h"

typedef struct {
	RT_OpBase op;
	const Apply *op_desc;
	Record r;                       // Bound branch record.
	RT_OpBase *bound_branch;        // Bound branch.
	RT_OpBase *rhs_branch;          // Right-hand branch.
	RT_Argument *op_arg;            // Right-hand branch tap.
} RT_Apply;

RT_OpBase *RT_NewApplyOp(const RT_ExecutionPlan *plan, const Apply *op_desc);
