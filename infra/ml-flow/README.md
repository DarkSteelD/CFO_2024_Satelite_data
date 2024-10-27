# ML Flow

---

! Мы используем инфраструктуру нашей лаборатори, однако ниже приведены комманды из конфлюинса по развертыванию базового кластера:

---

Добавим репозиторий ML Flow:

```bash
helm repo add community-charts https://community-charts.github.io/helm-charts
helm repo update
```

Получим список достпных нод в кластере чтобы ML Flow находился только на Master Node:

```bash
kubectl get nodes --show-labels
NAME                         STATUS   ROLES                  AGE   VERSION        LABELS
airflow-celery-cpu-mode      Ready    <none>                 46h   v1.30.5+k3s1   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/instance-type=k3s,beta.kubernetes.io/os=linux,gpu=false,kubernetes.io/arch=amd64,kubernetes.io/hostname=airflow-celery-cpu-mode,kubernetes.io/os=linux,node.kubernetes.io/instance-type=k3s
airflowcelery-gpu-p4-node    Ready    <none>                 46h   v1.30.5+k3s1   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/instance-type=k3s,beta.kubernetes.io/os=linux,gpu=true,kubernetes.io/arch=amd64,kubernetes.io/hostname=airflowcelery-gpu-p4-node,kubernetes.io/os=linux,node.kubernetes.io/instance-type=k3s
aorflow-celery-master-node   Ready    control-plane,master   46h   v1.30.5+k3s1   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/instance-type=k3s,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=aorflow-celery-master-node,kubernetes.io/os=linux,node-role.kubernetes.io/control-plane=true,node-role.kubernetes.io/master=true,node.kubernetes.io/instance-type=k3s
```

Создадим область видимости mlflow для k8s:

```bash
kubectl create namespace mlflow
```

Установим ML Flow:

```bash
helm install mlflow-service community-charts/mlflow \
  --namespace mlflow \
  --set replicaCount=1 \
  --set service.type=LoadBalancer \
  --set service.port=5000 \
  --set s3.bucket=mlmodels \
  --set s3.region= \
  --set s3.endpoint=https://192.168.1.2:9000 \
  --set s3.accessKey= \
  --set s3.secretKey= \
  --set nodeSelector."kubernetes\.io/hostname"=aorflow-celery-master-node
```