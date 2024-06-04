from abc import ABC, abstractmethod, abstractproperty, abstractclassmethod
from datetime import datetime
import textwrap


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:

    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = '001'
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou você não tem saldo suficiente @@@")

        elif valor > 0:
            self._saldo -= valor
            print("\nDepósito realizado com sucesso")
            return True
        
        else:
            print('\n@@@ Operação falhou, o valor informado é inválido @@@')
        return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n Depósito realizado com sucesso ")
        else:
            print("\n @@@ Operação falhou! o valor informado é invalido @@@")
            return False
        
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
            numero_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])

            excedeu_limite = valor > self.limite
            excedeu_saques = numero_saques > self.limite_saques

            if excedeu_limite:
                print("\n@@@ Operação falhou! O valor do saque excede o limite de 500 R$ @@@")

            elif excedeu_saques:
                print("\n @@@ Operação falhou! Número máximo de saques excedido @@@")
            
            else:
                return super().sacar(valor)
            
            return False
        
    def __str__(self):
        return f"Agência:\t{self.agencia}\nCC:\t\t{self.numero}\nTitular:\t{self.cliente.nome}"
        
class Historico():
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
        {
            "tipo": transacao.__class__.__name__,
            "valor":transacao.valor,
            "data": datetime.now().strftime("%d-%m-%y %H:%M:%S"),

        }
    )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu_text = """
    ||===================== MENU =====================||
    [d]      Depositar 
    [s]      Sacar  
    [e]      Extrato        
    [nc]     Nova conta
    [lc]     Listar contas       
    [nu]     Novo usuário
    [q]      Sair
    """
    return menu_text

def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)
    

def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    print("\n=============================================================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = 'Não foram realizados movimentações. '
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR${transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("\n=============================================================")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado @@@")
        return
    
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)

    print("\n=== Conta criada com sucesso!")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(conta)

def filtrar_cliente(cpf, clientes):
    # Filtrar a lista de clientes com base no CPF
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]

def sair():
    print("O Banco ProtectB agradece sua atenção....Até a próxima!")
    return False

def criar_cliente(clientes, contas):  # Adicione contas como um parâmetro
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cadastro com esse CPF! @@@")
        return
    
    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (Logradouro, nº - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")

    criar_conta_para_cliente(cliente, contas)  # Passe contas como argumento

def criar_conta_para_cliente(cliente, contas):  # Adicione contas como um parâmetro
    opcao = input("Deseja criar uma conta para este cliente? (s/n): ").lower()

    if opcao == 's':
        numero_conta = len(contas) + 1
        conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
        contas.append(conta)
        cliente.adicionar_conta(conta)

        print("\n=== Conta criada com sucesso!")


def main():
    clientes = []
    contas = []

    while True:
        print(menu())  # Exibir o menu para o usuário
        opcao = input("Escolha uma opção: ").lower()  # Capturar a entrada do usuário e converter para minúsculas

        if opcao == 'e':
            exibir_extrato(clientes)

        elif opcao == 's':
            sacar(clientes)

        elif opcao == 'd':
            depositar(clientes)

        elif opcao == 'lc':
            listar_contas(contas)

        if opcao == 'nc':
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == 'nu':
            criar_cliente(clientes, contas)
        elif opcao == 'q':
            if not sair():
                break

if __name__ == "__main__":
    main()
