#coding=utf-8
#导入
import redis
#隐式链接
r = redis.StrictRedis()
#显式链接
# r = redis.StrictRedis(host='127.0.0.1',port=6379,db=0)
#get 和set设置 
r.set('color','red')
r.get('color')
#HMSET  和 HGETALL 使用
r.hmset('dict',{'name':'anaf'})
people = r.hgetall('dict')
print people   #显示出字典{'name':'anaf'}
#管道的使用方式和事务相同，但是创建的时候需要加上参数transaction=False
pipe = r.pipeline(transaction=False)
#事务和管道还支持链式调用
result = r.pipeline().set('color','red'),.get('color').execute()




