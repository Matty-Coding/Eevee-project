## Esecuzione del progetto in locale

Lanciare i seguenti comandi dal path della cartella `backend`

## Ambiente virtuale

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```

```bash
python.exe -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

## Database

```bash
alembic revision --autogenerate -m "first migration"
```

```bash
alembic upgrade head
```

### Per cancellare tutto e ricrearlo

```bash
alembic downgrade base
```

```bash
alembic upgrade head
```

## Caricare i dati nel database

```bash
python -m scripts.load_data
```

## Creare profilo

```bash
python -m scripts.create_user_cli --username HellKiche --password TuaPassword
```

## Configurare .env

Creare un file `.env` in `backend` e copiare il contenuto di `.env.example`

ACCESS_TOKEN inserire un valore intero, corrisponde alla durata in minuti
REFRESH_TOKEN inserire un valore intero, corrisponde alla durata in giorni

Per generare token randomici per le key:

```bash
# aprire interprete di python
python
```

```bash
from secrets import token_urlsafe
token_urlsafe(64) # specificare la lunghezza
```