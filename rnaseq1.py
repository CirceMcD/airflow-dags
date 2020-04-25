"""
RNASeq 1
"""
import os

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.kubernetes.volume import Volume
from airflow.contrib.kubernetes.volume_mount import VolumeMount


##
# Persistent Volume Configuration
##

# Input sample table
input_sample_config= {
    'persistentVolumeClaim':
      {
        'claimName': 'pvc-input'
      }
    }

input_sample_volume = Volume(name='input-sample-mount', configs=input_sample_config)
input_sample_mount = VolumeMount('input-sample-mount',
                                mount_path='/rnaseq',
                                sub_path=None,
                                read_only=True)

## Reference Volume
input_ref_config= {
    'persistentVolumeClaim':
      {
        'claimName': 'pvc-references'
      }
    }

input_ref_volume = Volume(name='reference-mount', configs=input_ref_config)
input_ref_mount = VolumeMount('reference-mount',
                              mount_path='/rnaseq/ref',
                              sub_path=None,
                              read_only=True)

# Input Data Volume
input_data_config= {
    'persistentVolumeClaim':
      {
        'claimName': 'pvc-input'
      }
    }

input_data_volume = Volume(name='input-mount', configs=input_data_config)
input_data_mount = VolumeMount('input-mount',
                                mount_path='/rnaseq/data',
                                sub_path=None,
                                read_only=True)

## Output Volume
output_config= {
    'persistentVolumeClaim':
      {
        'claimName': 'pvc-output'
      }
    }

output_volume = Volume(name='output-mount', configs=output_config)
output_mount = VolumeMount('output-mount',
                            mount_path='/rnaseq/output',
                            sub_path=None,
                            read_only=False)


args = {
    'owner': 'airflow',
    'start_date': days_ago(2)
}


##
# RNA Seq 1
##
with DAG(
    dag_id='rnaseq1',
    default_args=args,
    schedule_interval=None,
    tags=['example'],
) as dag:

    rna_seq = KubernetesPodOperator(
        task_id="rna_seq_fat",
        name = "rnaseq1_pipeline",
        namespace='default',
        image="airflow1.azurecr.io/rnaseq:202003",
        cmds=["bash /rnaseq/rnaseq2020.sh"],
        volumes=[input_ref_config, input_data_volume, input_sample_volume, output_volume],
        volume_mounts=[input_ref_mount, input_data_mount, input_sample_mount, output_mount],
        resources={'request_memory':'32Gi', 'request_cpu': '4000m'},
        is_delete_operator_pod=True
    )

    # Order for pipeline to do stuff
    ## ls mount > create files > write to files
    rna_seq
    
