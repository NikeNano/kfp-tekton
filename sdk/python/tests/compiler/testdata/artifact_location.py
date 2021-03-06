# Copyright 2020 kubeflow.org
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import kfp
from kfp import dsl
from kubernetes.client import V1SecretKeySelector


@dsl.pipeline(
    name="custom_artifact_location_pipeline",
    description="""A pipeline to demonstrate how to configure the artifact
    location for all the ops in the pipeline. The default parameters are
    set to run on the kubeflow namespace along with kfp""",
)
def custom_artifact_location(
    secret_name: str = "mlpipeline-minio-artifact",
    tag: str = '1.31.0',
    namespace: str = "kubeflow",
    bucket: str = "mlpipeline"
):

    # configures artifact location
    pipeline_artifact_location = dsl.ArtifactLocation.s3(
        bucket=bucket,
        endpoint="minio-service.%s:9000" % namespace,  # parameterize minio-service endpoint
        insecure=True,
        access_key_secret=V1SecretKeySelector(name=secret_name, key="accesskey"),
        secret_key_secret={"name": secret_name, "key": "secretkey"},  # accepts dict also
    )

    # set pipeline level artifact location
    dsl.get_pipeline_conf().set_artifact_location(pipeline_artifact_location)

    # artifacts in this op are stored to endpoint `minio-service.<namespace>:9000`
    op = dsl.ContainerOp(name="generate-output", image="busybox:%s" % tag,
                         command=['sh', '-c', 'echo hello > /tmp/output.txt'],
                         file_outputs={'output': '/tmp/output.txt'})


if __name__ == '__main__':
    from kfp_tekton.compiler import TektonCompiler
    TektonCompiler().compile(custom_artifact_location, __file__.replace('.py', '.yaml'), enable_artifacts=True)
