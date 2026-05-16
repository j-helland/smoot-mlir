pub(crate) fn mul_units(lhs: &str, rhs: &str) -> Result<String, String> {
    if lhs.is_empty() || lhs == "dimensionless" {
        return Ok(rhs.to_string());
    }

    if rhs.is_empty() || rhs == "dimensionless" {
        return Ok(lhs.to_string());
    }

    if lhs == "meter / second" && rhs == "second" {
        return Ok("meter".to_string());
    }

    if lhs == "second" && rhs == "meter / second" {
        return Ok("meter".to_string());
    }

    Ok(format!("{lhs} * {rhs}"))
}

pub(crate) fn add_units(lhs: &str, rhs: &str) -> Result<String, String> {
    if lhs == rhs {
        Ok(lhs.to_string())
    } else {
        Err(format!("cannot add units `{lhs}` and `{rhs}`"))
    }
}
