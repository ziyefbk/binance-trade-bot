"""
配置加载模块
Agent 4 实现
"""

import yaml
from dataclasses import dataclass
from typing import List
import os


@dataclass
class APIConfig:
    key: str
    secret: str
    testnet: bool

    def validate(self):
        """验证 API 配置"""
        if not self.key or self.key == "your_api_key_here":
            raise ValueError("API key 未配置")
        if not self.secret or self.secret == "your_api_secret_here":
            raise ValueError("API secret 未配置")


@dataclass
class TriangularConfig:
    min_profit_percent: float
    max_position_usdt: float
    scan_interval_ms: int

    def validate(self):
        """验证三角套利配置"""
        if self.min_profit_percent <= 0:
            raise ValueError("min_profit_percent 必须大于 0")
        if self.max_position_usdt <= 0:
            raise ValueError("max_position_usdt 必须大于 0")
        if self.scan_interval_ms <= 0:
            raise ValueError("scan_interval_ms 必须大于 0")


@dataclass
class FundingRateConfig:
    min_rate_percent: float
    leverage: int
    position_percent: float

    def validate(self):
        """验证资金费率配置"""
        if self.min_rate_percent <= 0:
            raise ValueError("min_rate_percent 必须大于 0")
        if self.leverage < 1 or self.leverage > 10:
            raise ValueError("leverage 必须在 1-10 之间")
        if self.position_percent <= 0 or self.position_percent > 100:
            raise ValueError("position_percent 必须在 0-100 之间")


@dataclass
class RiskConfig:
    max_total_position_percent: float
    max_single_trade_percent: float
    stop_loss_percent: float

    def validate(self):
        """验证风险配置"""
        if self.max_total_position_percent <= 0 or self.max_total_position_percent > 100:
            raise ValueError("max_total_position_percent 必须在 0-100 之间")
        if self.max_single_trade_percent <= 0 or self.max_single_trade_percent > 100:
            raise ValueError("max_single_trade_percent 必须在 0-100 之间")
        if self.stop_loss_percent <= 0:
            raise ValueError("stop_loss_percent 必须大于 0")


@dataclass
class Config:
    api: APIConfig
    triangular: TriangularConfig
    funding_rate: FundingRateConfig
    risk: RiskConfig
    trading_pairs: List[str]

    def validate(self):
        """验证所有配置"""
        self.api.validate()
        self.triangular.validate()
        self.funding_rate.validate()
        self.risk.validate()

        if not self.trading_pairs:
            raise ValueError("trading_pairs 不能为空")


def load_config(path: str = "config/config.yaml") -> Config:
    """
    加载配置文件

    Args:
        path: 配置文件路径

    Returns:
        Config 对象

    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 配置项无效
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"配置文件不存在: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # 解析各个配置段
    api_config = APIConfig(**data['api'])
    triangular_config = TriangularConfig(**data['strategy']['triangular'])
    funding_config = FundingRateConfig(**data['strategy']['funding_rate'])
    risk_config = RiskConfig(**data['risk'])

    config = Config(
        api=api_config,
        triangular=triangular_config,
        funding_rate=funding_config,
        risk=risk_config,
        trading_pairs=data['trading_pairs']
    )

    # 验证配置
    config.validate()

    return config
