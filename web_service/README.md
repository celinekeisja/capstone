# Web Service App

Functionalities
-  Extracts metadata from a file submission and stores the metadata in a PostgreSQL database.
  - Extracts the file name, file type, file size, md5 hash, and sha1 hash of the file.
- Stores the files in a directory in the hosting machine. 
- Rejects duplicate file submissions.
- Allows clients to retrieve the metadata with the use of SHA-1 or MD5.
- Allows clients to update the metadata for a specific file with the use of SHA-1 or MD5.
- Allows clients to delete a file record.
  - Deletes the actual file stored in the machine as well.
  
Routes:
- GET http://10.5.95.65:8000/web_service_db (Read all file metadata records.)
- POST http://10.5.95.65:8000/web_service_db/upload (Uploads the file submitted through the harvester or form data.)

- GET http://10.5.95.65:8000/web_service_db/md5/<md5_hash_of_file> (Reads the metadata of the file record with the provided hash.)
- PUT http://10.5.95.65:8000/web_service_db/md5/<md5_hash_of_file> (Updates the file record with the given hash.)
- DELETE http://10.5.95.65:8000/web_service_db/md5/<md5_hash_of_file> (Deletes the file record and actual file in disk with the given hash.)

- GET http://10.5.95.65:8000/web_service_db/sha1/<sha1_hash_of_file> (Reads the metadata of the file record with the provided hash.)
- PUT http://10.5.95.65:8000/web_service_db/sha1/<sha1_hash_of_file> (Updates the file record with the given hash.)
- DELETE http://10.5.95.65:8000/web_service_db/sha1/<sha1_hash_of_file> (Deletes the file record and actual file in disk with the given hash.)
