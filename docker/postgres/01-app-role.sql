\getenv album_password ALBUM_DB_PASSWORD

CREATE ROLE album_app LOGIN PASSWORD :'album_password';
ALTER DATABASE electronic_photo_album OWNER TO album_app;
