from werkzeug.security import check_password_hash, generate_password_hash
pw = "men9a6D6"
hash = generate_password_hash(pw)

print(hash)