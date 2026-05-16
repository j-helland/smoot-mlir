use std::{
    ffi::{CStr, CString},
    os::raw::c_char,
    ptr,
};

use crate::algebra;

#[repr(C)]
pub struct UnitsStringResult {
    pub ok: bool,
    pub value: *mut c_char,
    pub error: *mut c_char,
}

#[unsafe(no_mangle)]
pub extern "C" fn units_mul(lhs: *const c_char, rhs: *const c_char) -> UnitsStringResult {
    ffi_result(|| {
        let lhs = read_c_str(lhs, "lhs")?;
        let rhs = read_c_str(rhs, "rhs")?;
        algebra::mul_units(lhs, rhs)
    })
}

#[unsafe(no_mangle)]
pub extern "C" fn units_add_result(lhs: *const c_char, rhs: *const c_char) -> UnitsStringResult {
    ffi_result(|| {
        let lhs = read_c_str(lhs, "lhs")?;
        let rhs = read_c_str(rhs, "rhs")?;
        algebra::add_units(lhs, rhs)
    })
}

#[unsafe(no_mangle)]
pub extern "C" fn units_free_string(ptr: *mut c_char) {
    if ptr.is_null() {
        return;
    }

    unsafe {
        drop(CString::from_raw(ptr));
    }
}

fn ffi_result<F>(f: F) -> UnitsStringResult
where
    F: FnOnce() -> Result<String, String>,
{
    match f() {
        Ok(value) => UnitsStringResult {
            ok: true,
            value: into_c_string(value),
            error: ptr::null_mut(),
        },
        Err(error) => UnitsStringResult {
            ok: false,
            value: ptr::null_mut(),
            error: into_c_string(error),
        },
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
