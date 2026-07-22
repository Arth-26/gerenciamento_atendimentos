from .db_context import get_banco_atual, ALIASES_VALIDOS


class MultiUBSRouter:
    """
    Todos os models do projeto vivem em AMBOS os bancos (ubs1 e ubs2)
    com o mesmo schema. A escolha de qual banco usar não depende do
    app/model (como nos routers "clássicos"), e sim do contexto da
    requisição atual (setado via set_banco_atual / futuro middleware).
    """

    def db_for_read(self, model, **hints):
        return get_banco_atual()

    def db_for_write(self, model, **hints):
        return get_banco_atual()

    def allow_relation(self, obj1, obj2, **hints):
        db_set = ALIASES_VALIDOS | {'default'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return obj1._state.db == obj2._state.db
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Aplica as migrations de TODOS os apps em ubs1 e ubs2,
        # já que o schema é replicado nos dois.
        return db in ALIASES_VALIDOS