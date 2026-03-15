use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn route_weight(c_edge: f64, t_edge: f64, ir_mode: f64) -> f64 {
    c_edge * t_edge * ir_mode
}
