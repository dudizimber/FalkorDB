/*
 * Copyright 2018-2021 Redis Labs Ltd. and Contributors
 *
 * This file is available under the Redis Labs Source Available License Agreement
 */

#pragma once

// Formatter for verbose (human-readable) replies
void ResultSet_ReplyWithVerboseHeader(RedisModuleCtx *ctx, const char **columns);

void ResultSet_EmitVerboseRow(RedisModuleCtx *ctx, GraphContext *gc,
							  SIValue **row, uint numcols);

