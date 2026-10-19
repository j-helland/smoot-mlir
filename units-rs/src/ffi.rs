use std::{
    ffi::{CStr, CString},
    os::raw::c_char,
    ptr,
    sync::LazyLock,
};

use smoot_rs::{registry::Registry, unit::Unit};

static REGISTRY: LazyLock<Result<Registry, String>> = LazyLock::new(|| {
    Registry::new_from_str(include_str!("../data/unit-definitions.txt")).map_err(|e| e.to_string())
});

#[allow(non_camel_case_types)]
pub struct Units_Unit {
    unit: Unit,
}

#[repr(C)]
pub struct Units_UnitResult {
    pub ok: bool,
    pub value: *mut Units_Unit,
    pub error: *mut c_char,
}

#[repr(C)]
pub struct Units_StringResult {
    pub ok: bool,
    pub value: *mut c_char,
    pub error: *mut c_char,
}

trait FfiResult<T> {
    fn ok(value: T) -> Self;
    fn err(error: String) -> Self;
}

impl FfiResult<*mut c_char> for Units_StringResult {
    fn ok(value: *mut c_char) -> Self {
        Self {
            ok: true,
            value,
            error: ptr::null_mut(),
        }
    }

    fn err(error: String) -> Self {
        Self {
            ok: false,
            value: ptr::null_mut(),
            error: into_c_string(error),
        }
    }
}

impl FfiResult<*mut Units_Unit> for Units_UnitResult {
    fn ok(value: *mut Units_Unit) -> Self {
        Self {
            ok: true,
            value,
            error: ptr::null_mut(),
        }
    }

    fn err(error: String) -> Self {
        Self {
            ok: false,
            value: ptr::null_mut(),
            error: into_c_string(error),
        }
    }
}

fn ffi_result<T, R, F>(f: F) -> R
where
    R: FfiResult<T>,
    F: FnOnce() -> Result<T, String>,
{
    match f() {
        Ok(value) => R::ok(value),
        Err(error) => R::err(error),
    }
}

#[unsafe(no_mangle)]
pub extern "C" fn units_parse_unit(expression: *const c_char) -> Units_UnitResult {
    ffi_result(|| {
        let expression = read_c_str(expression, "expression")?;
        let registry = REGISTRY.as_ref().map_err(|e| e.clone())?;
        let (factor, unit) = Unit::parse(registry, expression).map_err(|e| e.to_string())?;
        _ = factor; // TODO(jwh): handle factors
        Ok(Box::into_raw(Box::new(Units_Unit { unit })))
    })
}

#[unsafe(no_mangle)]
pub extern "C" fn units_format_unit(unit: *const Units_Unit) -> Units_StringResult {
    ffi_result(|| {
        let unit = read_unit(unit, "unit")?;
        Ok(into_c_string(unit.to_string()))
    })
}

fn read_unit<'a>(ptr: *const Units_Unit, name: &str) -> Result<&'a Unit, String> {
    if ptr.is_null() {
        return Err(format!("{name} pointer was null"));
    }
    unsafe { Ok(&(*ptr).unit) }
}

#[unsafe(no_mangle)]
pub extern "C" fn units_mul(lhs: *const Units_Unit, rhs: *const Units_Unit) -> Units_UnitResult {
    ffi_result(|| {
        let lhs = read_unit(lhs, "lhs")?;
        let rhs = read_unit(rhs, "rhs")?;

        let mut unit = lhs.clone();
        unit *= rhs;

        Ok(Box::into_raw(Box::new(Units_Unit { unit })))
    })
}

#[unsafe(no_mangle)]
pub extern "C" fn units_add(lhs: *const Units_Unit, rhs: *const Units_Unit) -> Units_UnitResult {
    ffi_result(|| {
        let lhs = read_unit(lhs, "lhs")?;
        let rhs = read_unit(rhs, "rhs")?;

        let unit = if lhs.is_compatible_with(rhs) {
            Ok(lhs.clone())
        } else {
            Err(format!("cannot add units `{lhs:?}` and `{rhs:?}`"))
        };

        unit.map(|unit| Units_Unit { unit })
            .map(Box::new)
            .map(Box::into_raw)
    })
}

/// # Safety
///
/// `ptr` must be null or a pointer returned by this library from
/// `Box::into_raw` for `Units_Unit`, and it must not have been freed already
#[unsafe(no_mangle)]
pub unsafe extern "C" fn units_free_unit(ptr: *mut Units_Unit) {
    if ptr.is_null() {
        return;
    }

    unsafe { drop(Box::from_raw(ptr)) }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn units_free_string(ptr: *mut c_char) {
    if ptr.is_null() {
        return;
    }

    unsafe {
        drop(CString::from_raw(ptr));
    }
}

fn read_c_str<'a>(ptr: *const c_char, name: &str) -> Result<&'a str, String> {
    if ptr.is_null() {
        return Err(format!("{name} pointer was null"));
    }

    unsafe {
        CStr::from_ptr(ptr)
            .to_str()
            .map_err(|err| format!("{name} was not valid UTF-8: {err}"))
    }
}

fn into_c_string(value: String) -> *mut c_char {
    match CString::new(value) {
        Ok(value) => value.into_raw(),
        Err(err) => {
            let sanitized = err
                .into_vec()
                .into_iter()
                .filter(|byte| *byte != 0)
                .collect::<Vec<_>>();

            CString::new(sanitized)
                .expect("interior NUL bytes were removed")
                .into_raw()
        }
    }
}
