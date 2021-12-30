class Ordem:
    def __init__(self):
       self.ativo = ''
       self.id = 0
       self.code = ''
       self.status = ''
       self.direcao = ''
       self.tipo_ordem = ''
       self.mensagem = ''
       self.preco_enviado = 0.0
       self.preco_executado = 0.0
       self.quantidade_enviada = 0.0
       self.quantidade_executada = 0.0
       self.descricao_status_executado ='filled'
       
