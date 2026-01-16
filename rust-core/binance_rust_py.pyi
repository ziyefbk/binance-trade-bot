"""
Python type hints for binance_rust_py module

This module provides high-performance Binance trading functionality
powered by Rust through PyO3 bindings.
"""

from typing import List, Optional


class BinanceEngine:
    """
    Main engine for interacting with Binance API.

    This class provides a high-level interface to Binance's trading functionality,
    including account management, order execution, and arbitrage opportunities detection.

    Example:
        >>> engine = BinanceEngine(api_key="xxx", api_secret="yyy", testnet=True)
        >>> engine.start_market_data(["BTCUSDT", "ETHUSDT"])
        >>> opportunities = engine.get_arbitrage_opportunities(min_profit_percent=0.15)
        >>> for opp in opportunities:
        ...     print(f"Found: {opp.path}, profit: {opp.profit_percent}%")
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool) -> None:
        """
        Initialize the Binance engine.

        Args:
            api_key: Your Binance API key
            api_secret: Your Binance API secret
            testnet: Whether to use the testnet (True) or mainnet (False)

        Raises:
            RuntimeError: If initialization fails
        """
        ...

    def start_market_data(self, symbols: List[str]) -> None:
        """
        Start real-time market data monitoring for specified symbols.

        Args:
            symbols: List of trading pairs to monitor (e.g., ["BTCUSDT", "ETHUSDT"])

        Raises:
            RuntimeError: If WebSocket connection fails
        """
        ...

    def stop_market_data(self) -> None:
        """
        Stop market data monitoring and close WebSocket connections.
        """
        ...

    def get_account_info(self) -> PyAccountInfo:
        """
        Retrieve account information including balances and trading permissions.

        Returns:
            Account information with all balances

        Raises:
            RuntimeError: If API request fails
        """
        ...

    def get_price(self, symbol: str) -> float:
        """
        Get the current cached price for a symbol.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")

        Returns:
            Current price, or 0.0 if not cached
        """
        ...

    def get_arbitrage_opportunities(self, min_profit_percent: float) -> List[PyArbitrageOpportunity]:
        """
        Scan for triangular arbitrage opportunities.

        Args:
            min_profit_percent: Minimum profit percentage threshold (e.g., 0.15 for 0.15%)

        Returns:
            List of arbitrage opportunities found
        """
        ...

    def execute_triangular_arbitrage(self, path: List[str], amount: float) -> PyArbitrageResult:
        """
        Execute a triangular arbitrage trade.

        Args:
            path: Trading path with 3 pairs (e.g., ["BTCUSDT", "ETHBTC", "ETHUSDT"])
            amount: Amount to invest in USDT

        Returns:
            Arbitrage execution result with profit information

        Raises:
            RuntimeError: If execution fails
        """
        ...

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str,
        price: Optional[float] = None
    ) -> PyExecutionResult:
        """
        Place a trading order.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            side: Order side, either "buy" or "sell"
            quantity: Order quantity
            order_type: Order type, either "market" or "limit"
            price: Price for limit orders (required if order_type is "limit")

        Returns:
            Order execution result

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If order execution fails
        """
        ...

    def cancel_order(self, symbol: str, order_id: int) -> None:
        """
        Cancel an existing order.

        Args:
            symbol: Trading pair symbol
            order_id: Order ID to cancel

        Raises:
            RuntimeError: If cancellation fails
        """
        ...

    def get_balances(self) -> List[PyBalance]:
        """
        Get all account balances.

        Returns:
            List of all asset balances

        Raises:
            RuntimeError: If API request fails
        """
        ...

    def get_ticker_price(self, symbol: str) -> float:
        """
        Get the current ticker price for a symbol using REST API.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")

        Returns:
            Current ticker price

        Raises:
            RuntimeError: If API request fails
        """
        ...


class PyArbitrageOpportunity:
    """
    Represents a triangular arbitrage opportunity.

    Attributes:
        path: Trading path (3 symbols)
        profit_percent: Expected profit percentage
        estimated_amount: Recommended investment amount
        execution_prices: Expected execution prices for each step
        timestamp: Opportunity detection timestamp (milliseconds)
    """

    path: List[str]
    profit_percent: float
    estimated_amount: float
    execution_prices: List[float]
    timestamp: int

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...


class PyArbitrageResult:
    """
    Result of a triangular arbitrage execution.

    Attributes:
        path: Trading path used
        initial_amount: Initial investment amount
        final_amount: Final amount after arbitrage
        profit_usdt: Profit in USDT
        profit_percent: Profit percentage
        execution_time_ms: Total execution time in milliseconds
    """

    path: List[str]
    initial_amount: float
    final_amount: float
    profit_usdt: float
    profit_percent: float
    execution_time_ms: int

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...


class PyExecutionResult:
    """
    Result of an order execution.

    Attributes:
        order_id: Order ID assigned by exchange
        symbol: Trading pair symbol
        executed_qty: Quantity that was executed
        avg_price: Average execution price
        commission: Trading fee paid
        execution_time_ms: Execution time in milliseconds
        success: Whether the order was successful
        error: Error message if failed, None if successful
    """

    order_id: int
    symbol: str
    executed_qty: float
    avg_price: float
    commission: float
    execution_time_ms: int
    success: bool
    error: Optional[str]

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...


class PyBalance:
    """
    Account balance for a single asset.

    Attributes:
        asset: Asset symbol (e.g., "BTC", "USDT")
        free: Free (available) balance
        locked: Locked balance (in orders)
    """

    asset: str
    free: float
    locked: float

    @property
    def total(self) -> float:
        """Total balance (free + locked)"""
        ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...


class PyAccountInfo:
    """
    Account information including all balances and permissions.

    Attributes:
        balances: List of all asset balances
        can_trade: Whether the account has trading permission
    """

    balances: List[PyBalance]
    can_trade: bool

    def get_balance(self, asset: str) -> Optional[PyBalance]:
        """
        Get balance for a specific asset.

        Args:
            asset: Asset symbol (e.g., "BTC", "USDT")

        Returns:
            Balance object if found, None otherwise
        """
        ...

    def get_non_zero_balances(self) -> List[PyBalance]:
        """
        Get all balances with non-zero total amounts.

        Returns:
            List of non-zero balances
        """
        ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
