// 独立的 binance 模块集成测试

use binance_rust_py::binance::*;

#[cfg(test)]
mod binance_tests {
    use super::*;

    #[test]
    fn test_types_compilation() {
        // 测试类型是否能正确编译和使用
        let side = OrderSide::Buy;
        assert_eq!(side.to_string(), "BUY");
    }
}
