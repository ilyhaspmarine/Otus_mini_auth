# Домашнее задание №6
## Backend for frontends. Apigateway

### Вариант 1 (С КОДОМ)

#### Добавить в приложение аутентификацию и регистрацию пользователей.

### Здесь у нас сервис аутентификации. Реализует 3 сценария:
- Создание нового пользователя (запрос на auth/register)
- Аутентификация пользователя с генерацией JWT (запрос на auth/login)
- Валидация JWT-токена (запрос на auth/validate)

### ПОДГОТОВКА
#### в /etc/hosts прописываем
```
127.0.0.1 arch.homework 
```

#### Запускаем docker
любым вариантом, у меня docker desktop с виртуализацией VT-d

#### Запускаем minikube
```
minikube start --driver=docker
```

#### NGINX
Считам, что с прошлой домашки никуда не ушел из кластеа

### СТАВИМ ПРИЛОЖЕНИЕ
#### Генерируем закрытый и открытый ключи у себя на машине
```
openssl genrsa -out ./etc/keys/jwt-private.pem 2048
```
```
openssl rsa -in ./etc/keys/jwt-private.pem -pubout -out ./etc/keys/jwt-public.pem
```

#### Создаем namespace под сервис аутентификации
```
kubectl create namespace auth
```

#### "Внешняя" поставка секретов в кластер
##### Секрет с данными для подключения к БД
```
kubectl apply -f ./secret/secret.yaml -n auth
```
##### Секрет с ключами подписания токенов
```
kubectl create secret generic jwt-signing-keys --from-file=private.pem=./etc/keys/jwt-private.pem --from-file=public.pem=./etc/keys/jwt-public.pem -n auth
```

#### Переходим в директорию с чартом
```
cd ./auth-app
```

#### Качаем зависимости
```
helm dependency update
```

#### Возвращаемся в корень
```
cd ../
```

#### Ставимся и ждем, пока установка закончится
```
helm install <имя_релиза> auth-app -n auth --create-namespace
```

#### Включаем (и не закрываем терминал)
```
minikube tunnel
```

#### Проверяем health-check (в новом окне терминала)
```
curl http://arch.homework/auth/health/
```


### КАК УДАЛИТЬ ПРИЛОЖЕНИЕ
#### Сносим чарт и БД
```
helm uninstall <имя релиза> -n auth
```

#### Сносим секреты
```
kubectl delete secret auth-db-secret -n auth
kubectl delete secret jwt-signing-keys -n auth
```

#### Сносим PVC, оставшиеся от БД
```
kubectl delete pvc -l app.kubernetes.io/name=auth-postgresql,app.kubernetes.io/instance=<имя_релиза> -n auth
```

#### Сносим PV, оставшиеся от БД (если reclaimPolicy: Retain)
```
kubectl get pv -n auth
```
Смотрим вывод, узнаем <имя PV> (к сожалению, меток у него не будет - я проверил)
```
kubectl delete pv <имя PV> -n auth
```

### Готово!
