from app.utils import format_currency

def test_format_with_decimal():
    input_value = 59.9
    result = format_currency(input_value)

    assert result == "59,90"
    #vai revificar se o resultado é igual a 59,90, ou seja, se ele formatou o numero com duas casas decimais e substituiu o ponto por virgula

def test_format_currency_with_integer():
    assert format_currency(123)=="123,00"

def test_format_currency_with_zero():
    assert format_currency(0)=="0,00"