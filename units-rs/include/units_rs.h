#pragma once

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct UnitsStringResult {
  bool ok;
  char *value;
  char *error;
} UnitsStringResult;

UnitsStringResult units_mul(const char *lhs, const char *rhs);
UnitsStringResult units_add_result(const char *lhs, const char *rhs);

void units_free_string(char *ptr);

#ifdef __cplusplus
}
#endif
