from pwdlib import PasswordHash
# toda criptografia de senha é feita com a biblioteca pwdlib, que é uma biblioteca de hashing de senha segura e moderna. a ideia é nao precisar reinventar a roda e usar uma biblioteca que já implementa algoritmos de hashing de senha seguros, como Argon2, bcrypt e scrypt. O Argon2 é o algoritmo recomendado atualmente, pois é resistente a ataques de força bruta e ataques de hardware especializado.

# PasswordHash encapsula o algoritmo de hashing de senha.
# O Argon2 fica responsável pelo trabalho criptográfico.


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    # as bibliotecas de hashing de senha são projetadas para serem lentas, para dificultar ataques de força bruta. Portanto, não é necessário adicionar um salt manualmente, pois o Argon2 já faz isso internamente.
    """
    Gera um hash seguro para armazenar no banco.
    A senha original nunca deve ser armazenada.
    """
    return password_hasher.hash(password)