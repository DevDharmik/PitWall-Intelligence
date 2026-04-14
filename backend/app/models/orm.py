"""
app/models/orm.py
─────────────────
SQLAlchemy ORM models mapping to the PostgreSQL schema defined in etl/schema.sql.
"""

from datetime import date, time
from decimal import Decimal

from sqlalchemy import (
    Integer, String, Numeric, Date, Time, BigInteger,
    ForeignKey, UniqueConstraint, CheckConstraint, Index,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Circuit(Base):
    __tablename__ = "circuits"

    circuit_id:  Mapped[int]   = mapped_column(Integer, primary_key=True)
    circuit_ref: Mapped[str]   = mapped_column(String(50), nullable=False)
    name:        Mapped[str]   = mapped_column(String(100), nullable=False)
    location:    Mapped[str | None] = mapped_column(String(100))
    country:     Mapped[str | None] = mapped_column(String(100))
    lat:         Mapped[float | None]
    lng:         Mapped[float | None]
    alt:         Mapped[int | None]
    url:         Mapped[str | None] = mapped_column(String(500))

    races: Mapped[list["Race"]] = relationship(back_populates="circuit")


class Race(Base):
    __tablename__ = "races"

    race_id:    Mapped[int]       = mapped_column(Integer, primary_key=True)
    season:     Mapped[int]       = mapped_column(Integer, nullable=False)
    round:      Mapped[int]       = mapped_column(Integer, nullable=False)
    circuit_id: Mapped[int | None] = mapped_column(ForeignKey("circuits.circuit_id"))
    name:       Mapped[str]       = mapped_column(String(100), nullable=False)
    date:       Mapped[date | None]
    time:       Mapped[time | None]
    url:        Mapped[str | None] = mapped_column(String(500))

    circuit:  Mapped["Circuit"]    = relationship(back_populates="races")
    results:  Mapped[list["Result"]]    = relationship(back_populates="race")
    qualifyings: Mapped[list["Qualifying"]] = relationship(back_populates="race")
    pit_stops:   Mapped[list["PitStop"]]    = relationship(back_populates="race")


class Constructor(Base):
    __tablename__ = "constructors"

    constructor_id:  Mapped[int] = mapped_column(Integer, primary_key=True)
    constructor_ref: Mapped[str] = mapped_column(String(50), nullable=False)
    name:            Mapped[str] = mapped_column(String(100), nullable=False)
    nationality:     Mapped[str | None] = mapped_column(String(50))
    url:             Mapped[str | None] = mapped_column(String(500))

    results:    Mapped[list["Result"]]      = relationship(back_populates="constructor")
    bvi_scores: Mapped[list["BviScore"]]    = relationship(back_populates="constructor")


class Driver(Base):
    __tablename__ = "drivers"

    driver_id:  Mapped[int] = mapped_column(Integer, primary_key=True)
    driver_ref: Mapped[str] = mapped_column(String(50), nullable=False)
    number:     Mapped[str | None] = mapped_column(String(5))
    code:       Mapped[str | None] = mapped_column(String(3))
    forename:   Mapped[str] = mapped_column(String(50), nullable=False)
    surname:    Mapped[str] = mapped_column(String(50), nullable=False)
    dob:        Mapped[date | None]
    nationality: Mapped[str | None] = mapped_column(String(50))
    url:        Mapped[str | None] = mapped_column(String(500))

    results:    Mapped[list["Result"]]      = relationship(back_populates="driver")
    qualifyings: Mapped[list["Qualifying"]] = relationship(back_populates="driver")
    pit_stops:  Mapped[list["PitStop"]]     = relationship(back_populates="driver")


class Result(Base):
    __tablename__ = "results"

    result_id:          Mapped[int]           = mapped_column(Integer, primary_key=True)
    race_id:            Mapped[int]           = mapped_column(ForeignKey("races.race_id"), nullable=False)
    driver_id:          Mapped[int]           = mapped_column(ForeignKey("drivers.driver_id"), nullable=False)
    constructor_id:     Mapped[int]           = mapped_column(ForeignKey("constructors.constructor_id"), nullable=False)
    number:             Mapped[str | None]    = mapped_column(String(5))
    grid:               Mapped[int | None]
    position:           Mapped[int | None]
    position_text:      Mapped[str | None]    = mapped_column(String(5))
    position_order:     Mapped[int | None]
    points:             Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    laps:               Mapped[int | None]
    time:               Mapped[str | None]    = mapped_column(String(20))
    milliseconds:       Mapped[int | None]    = mapped_column(BigInteger)
    fastest_lap:        Mapped[int | None]
    rank:               Mapped[int | None]
    fastest_lap_time:   Mapped[str | None]    = mapped_column(String(20))
    fastest_lap_speed:  Mapped[str | None]    = mapped_column(String(20))
    status_id:          Mapped[int | None]

    race:        Mapped["Race"]        = relationship(back_populates="results")
    driver:      Mapped["Driver"]      = relationship(back_populates="results")
    constructor: Mapped["Constructor"] = relationship(back_populates="results")


class Qualifying(Base):
    __tablename__ = "qualifying"

    qualify_id:     Mapped[int] = mapped_column(Integer, primary_key=True)
    race_id:        Mapped[int] = mapped_column(ForeignKey("races.race_id"), nullable=False)
    driver_id:      Mapped[int] = mapped_column(ForeignKey("drivers.driver_id"), nullable=False)
    constructor_id: Mapped[int] = mapped_column(ForeignKey("constructors.constructor_id"), nullable=False)
    number:         Mapped[int | None]
    position:       Mapped[int | None]
    q1:             Mapped[str | None] = mapped_column(String(20))
    q2:             Mapped[str | None] = mapped_column(String(20))
    q3:             Mapped[str | None] = mapped_column(String(20))

    race:   Mapped["Race"]   = relationship(back_populates="qualifyings")
    driver: Mapped["Driver"] = relationship(back_populates="qualifyings")


class PitStop(Base):
    __tablename__ = "pit_stops"

    stop_id:      Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    race_id:      Mapped[int] = mapped_column(ForeignKey("races.race_id"), nullable=False)
    driver_id:    Mapped[int] = mapped_column(ForeignKey("drivers.driver_id"), nullable=False)
    stop:         Mapped[int] = mapped_column(Integer, nullable=False)
    lap:          Mapped[int | None]
    time:         Mapped[time | None]
    duration:     Mapped[str | None] = mapped_column(String(20))
    milliseconds: Mapped[int | None]

    race:   Mapped["Race"]   = relationship(back_populates="pit_stops")
    driver: Mapped["Driver"] = relationship(back_populates="pit_stops")


class BviScore(Base):
    __tablename__ = "bvi_scores"
    __table_args__ = (
        UniqueConstraint("constructor_id", "season", name="uq_bvi_constructor_season"),
        CheckConstraint("tier IN (1, 2, 3)", name="ck_bvi_tier"),
    )

    score_id:        Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    constructor_id:  Mapped[int]           = mapped_column(ForeignKey("constructors.constructor_id"), nullable=False)
    season:          Mapped[int]           = mapped_column(Integer, nullable=False)
    total_points:    Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    wins:            Mapped[int | None]
    podiums:         Mapped[int | None]
    entries:         Mapped[int | None]
    dnf_rate:        Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    pts_finish_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    perf_score:      Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    cons_score:      Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    expo_score:      Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    bvi:             Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    tier:            Mapped[int | None]

    constructor: Mapped["Constructor"] = relationship(back_populates="bvi_scores")
