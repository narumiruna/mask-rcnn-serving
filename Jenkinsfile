import groovy.transform.Field

def shouldDeploy () {
    switch (env.BRANCH_NAME) {
        case ~/(.+-)?rc(-.+)?$/:
        case 'develop':
        case 'master':
            return true
        default:
            return false
    }
}

// Get image anchor tag name from the current branch name
// When using "Discover Pull Requests", the branch name will be replaced as the Pull Request Name
def getAnchorTag(String branchName) {
    return branchName.replaceAll("[^A-Za-z0-9.]", "-").toLowerCase()
}

def getTag(String branchName) {
    return getAnchorTag(branchName) + "-" + env.GIT_COMMIT.substring(0, 8)
}

def getImageName () {
    return "${env.GCP_DOCKER_REGISTRY}/${env.GCP_PROJECT}/mask-rcnn-serving"
}

def getClusterName(String branchName) {
    switch (branchName) {
        case ~/(.+-)?rc(-.+)?/:
            return "aurora-staging"
        case 'develop':
            return "aurora-dev"
        case 'master':
            return "aurora-prod"
        default:
            def message = "There is no cluster mapping to the branch ${branchName}."
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
        GCP_DOCKER_REGISTRY = "asia.gcr.io"
        GCP_PROJECT = "linker-aurora"
        GCP_ZONE =  "asia-east1-a"
    }
    stages {
        stage("Build Image"){
            parallel {
                stage('cpu') {
                    agent any
                    steps {
                        script {
                            def tag = getImageName() + ":" + getTag(env.BRANCH_NAME)
                            def image = docker.build(tag, ".")

                            withCredentials([
                                file(credentialsId: 'jenkins-aurora-sa.json', variable: 'JSON_SA')
                            ]) {
                                sh 'docker login -u _json_key --password-stdin https://asia.gcr.io < $JSON_SA'
                            }

                            if (shouldDeploy()) {
                                image.push()
                                image.push(getAnchorTag(env.BRANCH_NAME))
                                sh "docker rmi ${getImageName()}:${getAnchorTag(env.BRANCH_NAME)}"
                            }

                            sh "docker rmi ${tag}"
                        }
                    }
                }
                stage('gpu') {
                    agent any
                    steps {
                        script {
                            def tag = getImageName() + ":" + getTag(env.BRANCH_NAME) + "-gpu"
                            def image = docker.build(tag, "--file Dockerfile.gpu .")

                            withCredentials([
                                file(credentialsId: 'jenkins-aurora-sa.json', variable: 'JSON_SA')
                            ]) {
                                sh 'docker login -u _json_key --password-stdin https://asia.gcr.io < $JSON_SA'
                            }

                            if (shouldDeploy()) {
                                image.push()
                                image.push(getAnchorTag(env.BRANCH_NAME) + "-gpu")
                                sh "docker rmi ${getImageName()}:${getAnchorTag(env.BRANCH_NAME)}-gpu"
                            }

                            sh "docker rmi ${tag}"
                        }
                    }
                }
            }
        }
        stage('Deploy') {
            agent any
            when {
                beforeAgent true
                expression { -> shouldDeploy() }
            }
            steps {
                script {
                    withEnv([
                        "KUBECONFIG=/var/lib/jenkins/.kube/config.${getClusterName(env.BRANCH_NAME)}"
                    ]) {
                        sh "gcloud container clusters get-credentials --project ${env.GCP_PROJECT} --zone ${env.GCP_ZONE} ${getClusterName(env.BRANCH_NAME)}"
                        sh "kubectl apply -f kubernetes/pvc.yaml"
                        sh "kubectl apply -f kubernetes/deployment.yaml"
                        sh "kubectl apply -f kubernetes/service.yaml"
                    }
                }
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
                if (shouldDeploy()) {
                    // message += " <!here>"
                    slackSend channel: '#01_aurora', color: 'danger', message: message
                }
            }
        }
    }
}
