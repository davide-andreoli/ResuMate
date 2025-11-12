from app.api.main import app


def main():
    import uvicorn

    uvicorn.run(app)


if __name__ == "__main__":
    main()
