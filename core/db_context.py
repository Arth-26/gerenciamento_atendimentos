import threading
from contextlib import contextmanager

_thread_locals = threading.local()

ALIASES_VALIDOS = {'ubs1', 'ubs2'}


def set_banco_atual(alias):
    if alias not in ALIASES_VALIDOS:
        raise ValueError(f"Alias de banco inválido: {alias!r}")
    _thread_locals.db_alias = alias


def get_banco_atual():
    return getattr(_thread_locals, 'db_alias', 'ubs2')  # fallback seguro


def limpar_banco_atual():
    if hasattr(_thread_locals, 'db_alias'):
        del _thread_locals.db_alias


@contextmanager
def usando_banco(alias):
    """Útil pra testes e scripts manuais, antes de existir o middleware."""
    set_banco_atual(alias)
    try:
        yield
    finally:
        limpar_banco_atual()