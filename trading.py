from uteis.util import Util
from uteis.ordem import Ordem
from uteis.corretora import Corretora

corrBinance = Corretora('Binance')


ordem_venda_limitada = Ordem()

ordem_venda_limitada.quantidade_enviada = 4
ordem_venda_limitada.preco_enviado = 7
ordem_venda_limitada.tipo_ordem = 'market'

ret_compra = corrBinance.enviar_ordem_venda(ordem_venda_limitada, Util.CCYXRP(), Util.CCYBRL())



