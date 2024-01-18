resource "helm_release" "dremio-dataset-query" {
  name       = "dremio-dataset-query"
  chart      = "/chart"
  namespace  = "dremio-dataset-query-ns"
  create_namespace = true
}