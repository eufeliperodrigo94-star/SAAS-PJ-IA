from app.repositories.documents_repo import _sanitize_filename


def test_sanitize_filename_keeps_simple_names():
    assert _sanitize_filename("contrato-social.pdf") == "contrato-social.pdf"


def test_sanitize_filename_strips_path_segments():
    # Só o último segmento do caminho é preservado — nada antes da última
    # barra sobrevive, então um "../" não consegue escapar da pasta do objeto.
    assert _sanitize_filename("../../etc/passwd") == "passwd"
    assert _sanitize_filename("C:\\Users\\me\\secret.docx") == "secret.docx"


def test_sanitize_filename_replaces_unsafe_characters():
    assert _sanitize_filename("relatório (final)!.pdf") == "relat_rio_final_.pdf"


def test_sanitize_filename_never_returns_empty():
    assert _sanitize_filename("") == "arquivo"
    assert _sanitize_filename("...") == "arquivo"


def test_sanitize_filename_truncates_long_names():
    long_name = "a" * 500 + ".pdf"
    result = _sanitize_filename(long_name)
    assert len(result) <= 200
