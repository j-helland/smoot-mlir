module {
  func.func @valid(%v: f64, %t: f64) -> f64 {
    %0 = arith.mulf %v, %t {lhs_unit = "m/s", rhs_unit = "s"} : f64
    return %0 : f64
  }

  func.func @invalid(%v: f64, %t: f64) -> f64 {
    %0 = arith.addf %v, %t {lhs_unit = "m/s", rhs_unit = "s"} : f64
    return %0 : f64
  }
}
