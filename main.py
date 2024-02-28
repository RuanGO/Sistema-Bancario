import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import os
from datetime import datetime


class Conta:
    def __init__(self, login, senha, saldo, chave_pix):
        self.login = login
        self.senha = senha
        self.saldo = saldo
        self.extrato = []
        self.saques_realizados = 0
        self.chave_pix = chave_pix

    def depositar(self, valor, descricao):
        self.saldo += valor
        self.extrato.append(
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}: Depósito: R$ {valor:.2f} - Descrição: {descricao}")
        messagebox.showinfo("Depósito", "Depósito efetuado com sucesso!")

    def sacar(self, valor, descricao):
        if self.saques_realizados >= 3:
            messagebox.showerror("Erro", "Limite de saques diários excedido!")
            return

        if valor > 500:
            messagebox.showerror("Erro", "Limite de valor para saque diário excedido!")
            return

        if valor <= self.saldo:
            self.saldo -= valor
            self.extrato.append(
                f"{datetime.now().strftime('%d/%m/%Y %H:%M')}: Saque: R$ {valor:.2f} - Descrição: {descricao}")
            messagebox.showinfo("Saque", "Saque efetuado com sucesso!")
            self.saques_realizados += 1
        else:
            messagebox.showerror("Erro", "Saldo insuficiente!")

    def transferir_pix(self, valor, descricao, chave_pix_destino):
        if valor <= self.saldo:
            self.saldo -= valor
            self.extrato.append(
                f"{datetime.now().strftime('%d/%m/%Y %H:%M')}: Transferência PIX: R$ {valor:.2f} - Descrição: {descricao} - Chave PIX destino: {chave_pix_destino}")
            messagebox.showinfo("Transferência PIX", "Transferência PIX efetuada com sucesso!")
            # Atualiza o saldo da conta destino
            conta_destino = SistemaEletronico().get_conta_por_chave_pix(chave_pix_destino)
            if conta_destino:
                conta_destino.saldo += valor
                conta_destino.extrato.append(
                    f"{datetime.now().strftime('%d/%m/%Y %H:%M')}: Transferência PIX recebida: R$ {valor:.2f} - Descrição: {descricao} - Chave PIX origem: {self.chave_pix}")
        else:
            messagebox.showerror("Erro", "Saldo insuficiente!")

    def gerar_extrato(self):
        extrato_str = "\n".join(self.extrato)
        messagebox.showinfo("Extrato Bancário", f"Extrato bancário:\n{extrato_str}")

        # Pergunta se deseja salvar o extrato em um arquivo .txt
        resposta = messagebox.askyesno("Salvar Extrato", "Deseja salvar o extrato em um arquivo .txt?")
        if resposta:
            self.salvar_extrato_txt(extrato_str)

    def salvar_extrato_txt(self, extrato_str):
        # Abre uma janela de diálogo para selecionar o local de salvamento do arquivo
        filename = filedialog.asksaveasfilename(initialdir=os.path.expanduser("~/Desktop"),
                                                title="Salvar Extrato",
                                                defaultextension=".txt",
                                                filetypes=(("Arquivo de Texto", "*.txt"),))

        # Verifica se o usuário selecionou um local válido
        if filename:
            with open(filename, "w") as file:
                file.write(extrato_str)
            messagebox.showinfo("Extrato Salvo", "Extrato salvo com sucesso!")
        else:
            messagebox.showinfo("Aviso", "Nenhum arquivo selecionado. O extrato não foi salvo.")

    def get_divida(self):
        return self.divida

    def solicitar_emprestimo(self, valor):
        if self.saldo >= valor:
            messagebox.showerror("Erro", "Você já possui saldo suficiente para o empréstimo.")
            return

        if self.saldo - self.get_divida() >= valor:
            self.divida += valor * 1.08  # Adiciona o valor do empréstimo com juros à dívida
            self.saldo += valor  # Adiciona o valor do empréstimo ao saldo
            self.extrato.append(
                f"{datetime.now().strftime('%d/%m/%Y %H:%M')}: Empréstimo solicitado: R$ {valor:.2f}")
            messagebox.showinfo("Empréstimo", "Empréstimo solicitado com sucesso!")
        else:
            messagebox.showerror("Erro", "Empréstimo não aprovado devido ao valor total da dívida.")        


class SistemaEletronico:
    def __init__(self):
        self.contas = []

        # Criar contas de exemplo
        conta1 = Conta("Julia", "1234", 1000.00, "12345")
        conta2 = Conta("Ruan", "4321", 500.50, "54321")
        conta3 = Conta("Pedro", "0000", 2000.75, "98765")

        self.contas.append(conta1)
        self.contas.append(conta2)
        self.contas.append(conta3)

        self.conta_atual = None

        self.corpus_file = "D:/Projetos Programação/Projetos python/programa bancário/Corpus.txt"  # Caminho para o arquivo de corpus

    def efetuar_login(self):
        input_login = entry_login.get()
        input_senha = entry_senha.get()

        for conta in self.contas:
            if conta.login == input_login and conta.senha == input_senha:
                login_window.withdraw()
                self.conta_atual = conta
                self.abrir_menu_principal()
                messagebox.showinfo("Boas-vindas", f"Bem-vindo, {conta.login}!")
                return

        messagebox.showerror("Erro", "Login ou senha incorretos!")

    def abrir_menu_principal(self):
        menu_principal_window = tk.Tk()
        menu_principal_window.title("Menu Principal")
        menu_principal_window.geometry("580x480")

        def verificar_saldo():
            messagebox.showinfo("Saldo", f"Seu saldo é: R$ {self.conta_atual.saldo:.2f}")

        def depositar():
            valor = float(entry_valor.get())
            descricao = entry_descricao.get()
            self.conta_atual.depositar(valor, descricao)

        def sacar():
            valor = float(entry_valor.get())
            descricao = entry_descricao.get()
            self.conta_atual.sacar(valor, descricao)

        def transferir_pix():
            valor = float(entry_valor.get())
            descricao = entry_descricao.get()
            chave_pix_destino = entry_chave_pix_destino.get()
            self.conta_atual.transferir_pix(valor, descricao, chave_pix_destino)

        def gerar_extrato():
            self.conta_atual.gerar_extrato()

        def deslogar():
            menu_principal_window.destroy()
            self.conta_atual = None
            entry_login.delete(0, tk.END)
            entry_senha.delete(0, tk.END)
            login_window.deiconify()

        def solicitar_emprestimo():
            valor = float(entry_valor.get())
            sistema.conta_atual.solicitar_emprestimo(valor)
            verificar_saldo()

        label_titulo = tk.Label(menu_principal_window, text="Menu Principal", font=("Arial", 16))
        label_titulo.pack(pady=10)

        label_data_hora = tk.Label(menu_principal_window,
                                   text=f"Data e Hora Atual: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        label_data_hora.pack()

        button_verificar_saldo = tk.Button(menu_principal_window, text="Verificar Saldo", command=verificar_saldo)
        button_verificar_saldo.pack(pady=5)

        label_valor = tk.Label(menu_principal_window, text="Valor:")
        label_valor.pack(pady=5)

        entry_valor = tk.Entry(menu_principal_window)
        entry_valor.pack(pady=5)

        label_descricao = tk.Label(menu_principal_window, text="Descrição:")
        label_descricao.pack(pady=5)

        entry_descricao = tk.Entry(menu_principal_window)
        entry_descricao.pack(pady=5)

        label_chave_pix_destino = tk.Label(menu_principal_window, text="Chave Pix Destino:")
        label_chave_pix_destino.pack(pady=5)

        entry_chave_pix_destino = tk.Entry(menu_principal_window)
        entry_chave_pix_destino.pack(pady=5)

        button_depositar = tk.Button(menu_principal_window, text="Depositar", command=depositar)
        button_depositar.pack(pady=5)

        button_sacar = tk.Button(menu_principal_window, text="Sacar", command=sacar)
        button_sacar.pack(pady=5)

        button_transferir_pix = tk.Button(menu_principal_window, text="Transferir Pix", command=transferir_pix)
        button_transferir_pix.pack(pady=5)

        #button_emprestimo = tk.Button(menu_principal_window, text="Solicitar Empréstimo", command=solicitar_emprestimo)
        #button_emprestimo.pack(pady=5)

        button_gerar_extrato = tk.Button(menu_principal_window, text="Gerar Extrato", command=gerar_extrato)
        button_gerar_extrato.pack(pady=5)

        button_deslogar = tk.Button(menu_principal_window, text="Deslogar", command=deslogar)
        button_deslogar.pack(pady=10)


        menu_principal_window.mainloop()

    def load_corpus(self, file_path):
        corpus = []
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                corpus.append(line.strip())
        return corpus

    def search_answer(self, question, corpus):
        max_similarity = 0
        best_match = None

        for line in corpus:
            similarity = self.calculate_similarity(question, line)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = line

        return best_match if best_match else "Desculpe, não encontrei uma resposta para essa pergunta."

    def calculate_similarity(self, question, line):
        # Implemente o algoritmo de cálculo de similaridade (ex: tokenizador, cosseno, etc.)
        # Retorne um valor numérico representando a similaridade entre a pergunta e a linha do corpus
        # Quanto maior o valor, maior a similaridade
        return 0

    def get_conta_por_chave_pix(self, chave_pix):
        for conta in self.contas:
            if conta.chave_pix == chave_pix:
                return conta
        return None


sistema = SistemaEletronico()

# Cria a janela de login
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x180")

label_login = tk.Label(login_window, text="Login:")
label_login.pack(pady=5)

entry_login = tk.Entry(login_window)
entry_login.pack(pady=5)

label_senha = tk.Label(login_window, text="Senha:")
label_senha.pack(pady=5)

entry_senha = tk.Entry(login_window, show="*")
entry_senha.pack(pady=5)

button_login = tk.Button(login_window, text="Login", command=sistema.efetuar_login)
button_login.pack(pady=10)

login_window.mainloop()
