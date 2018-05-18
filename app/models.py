from app import db


class Ticker(db.Model):
    __tablename__ = "tickers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    insiders = db.relationship("Insider", backref="ticker", cascade="delete")
    history = db.relationship("History", backref="ticker", cascade="delete")

    def to_dict(self):
        data = {
            "id": self.id,
            "name": self.name,
        }
        return data

    def __repr__(self):
        return f"<Ticker: {self.name}>"


class History(db.Model):
    __tablename__ = "history"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    open = db.Column(db.Float(precision=2))
    high = db.Column(db.Float(precision=2))
    low = db.Column(db.Float(precision=2))
    close = db.Column(db.Float(precision=2))
    volume = db.Column(db.Integer)
    ticker_id = db.Column(db.Integer, db.ForeignKey("tickers.id", ondelete="CASCADE"), nullable=False)

    def to_dict(self):
        data = {
            "id": self.id,
            "date": self.date,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "ticker_id": self.ticker_id
        }
        return data

    def __repr__(self):
        return f"<History object: {self.date}-{self.open}-{self.high}-{self.low}-{self.close}-{self.volume}" \
               f"{self.ticker_id}>"


class Insider(db.Model):
    __tablename__ = "insiders"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    relation = db.Column(db.String(100))
    inner_id = db.Column(db.Integer)
    ticker_id = db.Column(db.Integer, db.ForeignKey("tickers.id", ondelete="CASCADE"), nullable=False)
    trades = db.relationship("InsiderTrade", backref="insider", cascade="delete")

    def to_dict(self):
        data = {
            "id": self.id,
            "name": self.name,
            "relation": self.relation,
            "inner_id": self.inner_id,
            "ticker_id": self.ticker_id,
            "trades": [trade.to_dict() for trade in self.trades]
        }
        return data

    def __repr__(self):
        return f"<Insider object: {self.id} - {self.name}>"


class InsiderTrade(db.Model):
    __tablename__ = "insider_trades"

    id = db.Column(db.Integer, primary_key=True)
    insider_id = db.Column(db.Integer, db.ForeignKey("insiders.id", ondelete="CASCADE"), nullable=False)
    last_date = db.Column(db.DateTime)
    transaction_type = db.Column(db.String(100))
    owner_type = db.Column(db.String(20))
    shares_traded = db.Column(db.Integer)
    last_price = db.Column(db.Float(precision=4))
    shares_held = db.Column(db.Integer)

    def to_dict(self):
        data = {
            "id": self.id,
            "insider_id": self.insider_id,
            "last_date": self.last_date,
            "transaction_type": self.transaction_type,
            "owner_type": self.owner_type,
            "shares_traded": self.shares_traded,
            "last_price": self.last_price,
            "shares_held": self.shares_held,
        }
        return data

    def __repr__(self):
        return f"<InsiderTradeData object: {self.last_date}-" \
               f"{self.transaction_type}-{self.owner_type}-{self.shares_traded}-{self.last_price}-{self.shares_held}" \
