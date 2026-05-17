#include "units_rs.h"

#include "gtest/gtest.h"

namespace {

TEST(UnitsRsAbiTest, ParsesMultipliesFormatsAndFreesUnits) {
  Units_UnitResult velocity = units_parse_unit("meter / second");
  ASSERT_TRUE(velocity.ok) << (velocity.error ? velocity.error : "");
  ASSERT_NE(velocity.value, nullptr);

  Units_UnitResult seconds = units_parse_unit("second");
  ASSERT_TRUE(seconds.ok) << (seconds.error ? seconds.error : "");
  ASSERT_NE(seconds.value, nullptr);

  Units_UnitResult product = units_mul(velocity.value, seconds.value);
  ASSERT_TRUE(product.ok) << (product.error ? product.error : "");
  ASSERT_NE(product.value, nullptr);

  Units_StringResult formatted = units_format_unit(product.value);
  ASSERT_TRUE(formatted.ok) << (formatted.error ? formatted.error : "");
  ASSERT_NE(formatted.value, nullptr);
  EXPECT_STREQ(formatted.value, "meter");

  units_free_string(formatted.value);
  units_free_unit(product.value);
  units_free_unit(seconds.value);
  units_free_unit(velocity.value);
}

TEST(UnitsRsAbiTest, ReportsInvalidAdd) {
  Units_UnitResult meter = units_parse_unit("meter");
  ASSERT_TRUE(meter.ok) << (meter.error ? meter.error : "");

  Units_UnitResult second = units_parse_unit("second");
  ASSERT_TRUE(second.ok) << (second.error ? second.error : "");

  Units_UnitResult sum = units_add(meter.value, second.value);
  ASSERT_FALSE(sum.ok);
  ASSERT_NE(sum.error, nullptr);

  units_free_string(sum.error);
  units_free_unit(second.value);
  units_free_unit(meter.value);
}

} // namespace
