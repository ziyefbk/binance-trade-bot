"""
三角套利策略
Agent 4 实现
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging
from itertools import permutations

logger = logging.getLogger(__name__)


@dataclass
class TriangularPath:
    """三角套利路径"""
    symbols: List[str]
    base_asset: str
    intermediate_asset: str
    quote_asset: str

    def __repr__(self):
        return f"TriangularPath({self.base_asset} → {self.intermediate_asset} → {self.quote_asset})"


class TriangularArbitrage:
    """三角套利策略类"""

    def __init__(self, engine, config):
        """
        初始化三角套利策略

        Args:
            engine: Rust BinanceEngine 实例
            config: TriangularConfig 配置
        """
        self.engine = engine
        self.config = config
        self.min_profit_threshold = config.min_profit_percent
        self.max_position_size = config.max_position_usdt
        self.scan_interval_ms = config.scan_interval_ms

        # 缓存生成的路径
        self.cached_paths: List[TriangularPath] = []

        logger.info(f"三角套利策略初始化: min_profit={self.min_profit_threshold}%, "
                   f"max_position={self.max_position_size} USDT")

    def generate_paths(self, trading_pairs: List[str]) -> List[TriangularPath]:
        """
        生成所有可能的三角套利路径

        思路:
        1. 从交易对列表中提取所有资产
        2. 找出所有可能的三角路径组合
        3. 验证路径的有效性

        Example:
            输入: ["BTCUSDT", "ETHBTC", "ETHUSDT"]
            输出: [
                TriangularPath(["BTCUSDT", "ETHBTC", "ETHUSDT"], "USDT", "BTC", "ETH"),
                TriangularPath(["ETHUSDT", "ETHBTC", "BTCUSDT"], "USDT", "ETH", "BTC")
            ]
        """
        if not trading_pairs:
            logger.warning("交易对列表为空，无法生成路径")
            return []

        # 构建交易对映射 {(base, quote): symbol}
        pair_map = {}
        assets = set()

        for symbol in trading_pairs:
            # 解析交易对
            base, quote = self._parse_symbol(symbol)
            if base and quote:
                pair_map[(base, quote)] = symbol
                assets.add(base)
                assets.add(quote)

        logger.info(f"发现 {len(assets)} 个资产: {sorted(assets)}")
        logger.info(f"发现 {len(pair_map)} 个交易对")

        paths = []

        # 对于每个基础资产(通常是 USDT)
        for start_asset in assets:
            # 尝试所有可能的中间资产组合
            other_assets = [a for a in assets if a != start_asset]

            for intermediate1 in other_assets:
                for intermediate2 in other_assets:
                    if intermediate1 == intermediate2:
                        continue

                    # 检查是否存在完整的三角路径
                    # Path: start → intermediate1 → intermediate2 → start
                    path_symbols = self._find_path(
                        start_asset, intermediate1, intermediate2, pair_map
                    )

                    if path_symbols and len(path_symbols) == 3:
                        path = TriangularPath(
                            symbols=path_symbols,
                            base_asset=start_asset,
                            intermediate_asset=intermediate1,
                            quote_asset=intermediate2
                        )
                        paths.append(path)

        # 去重 (有些路径可能是重复的)
        unique_paths = self._deduplicate_paths(paths)

        logger.info(f"生成了 {len(unique_paths)} 条有效的三角套利路径")
        for i, path in enumerate(unique_paths[:5]):  # 只显示前5条
            logger.debug(f"  路径 {i+1}: {path}")

        self.cached_paths = unique_paths
        return unique_paths

    def _parse_symbol(self, symbol: str) -> tuple[Optional[str], Optional[str]]:
        """
        解析交易对符号

        Example:
            "BTCUSDT" -> ("BTC", "USDT")
            "ETHBTC" -> ("ETH", "BTC")
        """
        # 常见的报价币种
        quote_assets = ["USDT", "BUSD", "BTC", "ETH", "BNB", "USDC"]

        for quote in quote_assets:
            if symbol.endswith(quote):
                base = symbol[:-len(quote)]
                if base:
                    return base, quote

        # 如果无法解析，返回 None
        logger.warning(f"无法解析交易对: {symbol}")
        return None, None

    def _find_path(self, start: str, mid1: str, mid2: str,
                   pair_map: Dict[tuple, str]) -> Optional[List[str]]:
        """
        查找从 start → mid1 → mid2 → start 的完整路径

        Returns:
            三个交易对的符号列表，如果路径不存在则返回 None
        """
        # Step 1: start → mid1
        symbol1 = pair_map.get((start, mid1)) or pair_map.get((mid1, start))
        if not symbol1:
            return None

        # Step 2: mid1 → mid2
        symbol2 = pair_map.get((mid1, mid2)) or pair_map.get((mid2, mid1))
        if not symbol2:
            return None

        # Step 3: mid2 → start
        symbol3 = pair_map.get((mid2, start)) or pair_map.get((start, mid2))
        if not symbol3:
            return None

        return [symbol1, symbol2, symbol3]

    def _deduplicate_paths(self, paths: List[TriangularPath]) -> List[TriangularPath]:
        """去除重复的路径"""
        seen = set()
        unique = []

        for path in paths:
            # 使用符号列表的 tuple 作为唯一标识
            key = tuple(sorted(path.symbols))
            if key not in seen:
                seen.add(key)
                unique.append(path)

        return unique

    def scan_opportunities(self) -> List[Dict]:
        """
        扫描当前的套利机会

        Returns:
            套利机会列表，每个机会包含:
            {
                "path": List[str],
                "profit_percent": float,
                "estimated_amount": float,
                "execution_prices": List[float],
                "timestamp": int
            }
        """
        try:
            # 调用 Rust 引擎扫描套利机会
            opportunities = self.engine.get_arbitrage_opportunities(
                self.min_profit_threshold
            )

            # 转换为字典格式
            result = []
            for opp in opportunities:
                result.append({
                    "path": opp.path,
                    "profit_percent": opp.profit_percent,
                    "estimated_amount": opp.estimated_amount,
                    "execution_prices": opp.execution_prices,
                    "timestamp": opp.timestamp
                })

            logger.info(f"发现 {len(result)} 个套利机会")
            return result

        except Exception as e:
            logger.error(f"扫描套利机会失败: {e}")
            return []

    def execute(self, opportunity: Dict) -> Dict:
        """
        执行套利

        Args:
            opportunity: 套利机会字典

        Returns:
            {
                "success": bool,
                "profit_usdt": float,
                "profit_percent": float,
                "execution_time_ms": int,
                "error": Optional[str]
            }
        """
        path = opportunity["path"]
        amount = self.calculate_position_size(opportunity)

        logger.info(f"执行三角套利: path={path}, amount={amount} USDT")

        try:
            # 调用 Rust 引擎执行套利
            result = self.engine.execute_triangular_arbitrage(path, amount)

            success = result.profit_usdt > 0

            if success:
                logger.info(f"套利成功! 利润: ${result.profit_usdt:.2f} "
                          f"({result.profit_percent:.3f}%), "
                          f"耗时: {result.execution_time_ms}ms")
            else:
                logger.warning(f"套利失败: 亏损 ${abs(result.profit_usdt):.2f}")

            return {
                "success": success,
                "profit_usdt": result.profit_usdt,
                "profit_percent": result.profit_percent,
                "execution_time_ms": result.execution_time_ms,
                "initial_amount": result.initial_amount,
                "final_amount": result.final_amount,
                "error": None
            }

        except Exception as e:
            error_msg = f"执行套利失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "profit_usdt": 0.0,
                "profit_percent": 0.0,
                "execution_time_ms": 0,
                "error": error_msg
            }

    def calculate_position_size(self, opportunity: Dict) -> float:
        """
        计算合适的仓位大小

        策略:
        1. 不超过配置的最大单笔限额
        2. 根据预期利润调整 (利润越高，仓位可以适当增大)
        3. 考虑市场流动性 (estimated_amount)

        Args:
            opportunity: 套利机会

        Returns:
            建议的投入金额 (USDT)
        """
        # 基础仓位 = 最大仓位
        base_position = self.max_position_size

        # 根据预期利润调整
        profit_percent = opportunity.get("profit_percent", 0)
        if profit_percent > 0.5:
            # 利润超过 0.5%，可以使用满仓
            adjusted_position = base_position
        elif profit_percent > 0.3:
            # 利润 0.3%-0.5%，使用 80%
            adjusted_position = base_position * 0.8
        else:
            # 利润较低，使用 50%
            adjusted_position = base_position * 0.5

        # 考虑估计金额 (流动性)
        estimated = opportunity.get("estimated_amount", adjusted_position)
        final_position = min(adjusted_position, estimated)

        logger.debug(f"仓位计算: base={base_position}, adjusted={adjusted_position:.2f}, "
                    f"final={final_position:.2f} USDT")

        return final_position
