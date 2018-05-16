from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, SelectField, IntegerField, validators

from app.utils import DATETIME_FORMAT


INCORRECT_DATA_MESSAGE = "Введите корректную дату"


class DateForm(FlaskForm):
    start_date = DateField("Начальная дата",
                           validators=[validators.DataRequired(message=INCORRECT_DATA_MESSAGE)],
                           format=DATETIME_FORMAT)
    end_date = DateField("Конечная дата",
                         validators=[validators.DataRequired(message=INCORRECT_DATA_MESSAGE)],
                         format=DATETIME_FORMAT)
    submit = SubmitField("Отправить")


class DeltaForm(FlaskForm):
    value = IntegerField("Изменение цены", validators=[validators.InputRequired(message="Введите число")],
                         render_kw={"placeholder": "Введите число"})
    type = SelectField("Выберите тип",
                        choices=[("open", "Open"), ("high", "High"), ("low", "Low"), ("close", "Close")])
    submit = SubmitField("Отправить")

