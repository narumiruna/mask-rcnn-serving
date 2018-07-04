def needDeploy () {
    switch (env.BRANCH_NAME) {
        case ~/(.+-)?rc(-.+)?/:
        case ~/develop/:
        case ~/master/:
            return true
        default:
            return false
    }
}

def getAnchorTag () {
    return env.BRANCH_NAME.replaceAll("[^A-Za-z0-9.]", "-").toLowerCase()
}

def getTag () {
    return getAnchorTag() + "-" + env.GIT_COMMIT.substring(0, 8)
}

def getImageName () {
    return "${env.GCP_DOCKER_REGISTRY}/${env.GCP_PROJECT}/mask-rcnn-serving"
}

def getClusterName() {
    switch (env.BRANCH_NAME) {
        case ~/(.+-)?rc(-.+)?/:
            return "aurora-staging"
        case ~/develop/:
            return "aurora-dev"
        case ~/master/:
            return "aurora-prod"
        default:
            def message = "${env.BRANCH_NAME} is not support to cluster."
            echo message
            throw new Exception(message)
    }

}

pipeline {
    agent none
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }
    environment {
        KUBECONFIG = "/var/lib/jenkins/.kube/config.aurora-dev"
        GCP_DOCKER_REGISTRY = "asia.gcr.io"
        GCP_PROJECT = "linker-aurora"
        GCP_ZONE =  "asia-east1-a"
    }
    stages {
        stage("Build Image"){
            parallel {
                stage('ubuntu') {
                    agent any
                    steps{
                        script {
                            checkout scm

                            def image = docker.build(getImageName(), "--file Dockerfile .")

                            withCredentials([
                                file(credentialsId: 'jenkins-aurora-sa.json', variable: 'JSON_SA')
                            ]) {
                                sh 'docker login -u _json_key --password-stdin https://asia.gcr.io < $JSON_SA'
                            }

                            image.push(getAnchorTag())
                            image.push(getTag())
                        }
                    }
                }
                stage('nvidia') {
                    agent any
                    steps{
                        script {
                            checkout scm

                            def image = docker.build(getImageName(), "--file Dockerfile.gpu .")

                            withCredentials([
                                file(credentialsId: 'jenkins-aurora-sa.json', variable: 'JSON_SA')
                            ]) {
                                sh 'docker login -u _json_key --password-stdin https://asia.gcr.io < $JSON_SA'
                            }

                            image.push(getAnchorTag() + "-nvidia")
                            image.push(getTag() + "-nvidia")
                        }
                    }
                }
            }
        }
        stage('Deploy') {
            agent any
            when {
                beforeAgent true
                expression { -> needDeploy() }
            }
            steps {
                checkout scm
                sh "gcloud container clusters get-credentials --project ${env.GCP_PROJECT} --zone ${env.GCP_ZONE} ${getClusterName()}"
                sh "kubectl replace -f kubernetes/deployment.yaml"
                sh "kubectl replace -f kubernetes/service.yaml"
            }
        }
    }
    post {
        success {
            script {
                def message =
                    "<https://jenkins.linkernetworks.co/job/mask-rcnn-serving/|mask-rcnn-serving> » " +
                    "<${env.JOB_URL}|${env.BRANCH_NAME}> » " +
                    "<${env.BUILD_URL}|#${env.BUILD_NUMBER}> passed."

                slackSend channel: '#09_jenkins', color: 'good', message: message
            }
        }
        failure {
            script {
                def message =
                    "<https://jenkins.linkernetworks.co/job/mask-rcnn-serving/|mask-rcnn-serving> » " +
                    "<${env.JOB_URL}|${env.BRANCH_NAME}> » " +
                    "<${env.BUILD_URL}|#${env.BUILD_NUMBER}> failed."

                slackSend channel: '#09_jenkins', color: 'danger', message: message

                if (needDeploy()) {
                    message += " <!here>"
                    slackSend channel: '#01_aurora', color: 'danger', message: message
                }
            }
        }
    }
}
