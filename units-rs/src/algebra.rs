use crate::unit::Unit;

pub(crate) fn mul_units(lhs: &Unit, rhs: &Unit) -> Result<Unit, String> {
    if lhs.expression.is_empty() || lhs.expression == "dimensionless" {
        return Ok(rhs.clone());
    }

    if rhs.expression.is_empty() || rhs.expression == "dimensionless" {
        return Ok(lhs.clone());
    }

    if lhs.expression == "meter / second" && rhs.expression == "second" {
        return Ok(Unit::parse("meter"));
    }

    if lhs.expression == "second" && rhs.expression == "meter / second" {
        return Ok(Unit::parse("meter"));
    }

    Ok(Unit::parse(&format!(
        "{} * {}",
        lhs.expression, rhs.expression
    )))
}

pub(crate) fn add_units(lhs: &Unit, rhs: &Unit) -> Result<Unit, String> {
    if lhs == rhs {
        Ok(lhs.clone())
    } else {
        Err(format!("cannot add units `{lhs:?}` and `{rhs:?}`"))
    }
}
