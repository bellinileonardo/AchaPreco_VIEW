select 
e.ean, 
i.nome ,
i.preco , 
i2.precopromocao,
(((i.preco - i2.precopromocao) / i.preco) * 100) ::int as desconto
from item i 
	inner join ean e 
	on i.id = e.iditem 
	inner  join itempromocao i2 
	on i.id = i2.iditem 
where i.desativado isnull 	
limit 100

select * from itempromocao i 
limit 100