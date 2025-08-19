from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Float, String, BigInteger, Index

class Base(DeclarativeBase):
    pass

class EquityPoint(Base):
    __tablename__ = "equity_points"
    ts: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # ms since epoch
    equity: Mapped[float] = mapped_column(Float, nullable=False)
    pnl: Mapped[float | None] = mapped_column(Float)
    pnl_pct: Mapped[float | None] = mapped_column(Float)

class Fill(Base):
    __tablename__ = "fills"
    id: Mapped[str] = mapped_column(String, primary_key=True)  # Alpaca activity id
    ts: Mapped[int] = mapped_column(BigInteger, index=True)    # ms since epoch
    symbol: Mapped[str] = mapped_column(String, index=True)
    side: Mapped[str] = mapped_column(String)                  # buy/sell
    qty: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    order_id: Mapped[str | None] = mapped_column(String)

Index("idx_fills_symbol_ts", Fill.symbol, Fill.ts)