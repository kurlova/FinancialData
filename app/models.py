from app import db


class Ticker(db.Model):
    __tablename__ = "tickers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    insiders = db.relationship("Insider", backref="ticker", cascade="delete")
    history = db.relationship("History", backref="ticker", cascade="delete")

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

    def __repr__(self):
        return f"<History object: {self.date}-{self.open}-{self.high}-{self.low}-{self.close}-{self.volume}"\
               f"{self.ticker_id}>"


class Insider(db.Model):
    __tablename__ = "insiders"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    inner_id = db.Column(db.Integer)
    relation = db.Column(db.String(100))
    last_date = db.Column(db.DateTime)
    transaction_type = db.Column(db.String(100))
    owner_type = db.Column(db.String(20))
    shares_traded = db.Column(db.Integer)
    last_price = db.Column(db.Float(precision=4))
    shares_held = db.Column(db.Integer)
    ticker_id = db.Column(db.Integer, db.ForeignKey("tickers.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"<InsiderData object: {self.name}-{self.inner_id}-{self.relation}-{self.last_date}-" \
               f"{self.transaction_type}-{self.owner_type}-{self.shares_traded}-{self.last_price}-{self.shares_held}" \
               f"{self.ticker_id}>"
