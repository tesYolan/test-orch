# This test script is utilized to do the following simple things.
# Pull an image
# Create a coontaineer on that image
# Run a task on that container
# Close that container.
# It is tested in python3.7 and latest docker SDK.
# https://docker-py.readthedocs.io/en/stable/
import docker
import grpc

import object_detection_pb2_grpc
import object_detection_pb2
import base64
class Orchestrator:
    def __init__(self):
        self.image_repos = {"yolov3-object-detection":"https://raw.githubusercontent.com/singnet/dnn-model-services/master/services/yolov3-object-detection/Dockerfile",
                            "cntk-image-reco":"https://raw.githubusercontent.com/singnet/dnn-model-services/master/services/cntk-image-recon/Dockerfile"}

        self.client = docker.from_env()

    def build(self, image_name):
        """
        This builds images specified using images.build option.

        :param image_name: the image from the self.image_repos that is going to be built.
        """
        img_ret, json_respone = self.client.images.build(path=self.image_repos[image_name],tag=image_name)
        for i in json_respone:
            print(i)

        # we need to capture the various issues. And inform the user about that. The output above is quite not
        # insightful.

    def create(self, image_name, argument, port):
        """
        This creates the container using the image name.

        The listing of the arguments is going to be tough. We need to make it specific that it would be good.

        :param argument: The startup arguments for the image.
        :param image_name: The image that is going to create a container
        """

        container = self.client.containers.run(image_name,ports={str(port):port}, command= argument, detach=True)

        #TODO find means to store this value.
        print(container.status)
        print(container.name)
        return container

    def delete(self, container):
        """
        Stop and Delete a container
        :param container:
        """
        container.stop()
        container.remove()

    def call(self, container, port):
        """
        Now, this is a bit tricky. Now we have created the containers. We have to call them using an image the user
        has submmited. Which creates this issue:
        - We have to include the grpc server in this code base. Or some kinda of adaptor that is similar to snetdapp.

        And how would this function scale is the main problem.

        For now; I have implemented the system using natively installed GRPC clients. But this won't scale and would
        make this kinda of organizatino bloated.
        :param container:
        """

        if container == 'yolo':
            channel = grpc.insecure_channel('localhost:'+str(port))
            stub = object_detection_pb2_grpc.DetectStub(channel)

            grpc_method = "detect"
            model = "yolov3"
            confidence = "0.7"



            request = object_detection_pb2.Input(model=model, confidence=confidence, img_path="https://raw.githubusercontent.com/singnet/dnn-model-services/master/docs/assets/users_guide/backpack_man_dog.jpg")
            response = stub.detect(request)

            print(response)

        # Another point that we need to discuss; we have to take this and change this to some format that would be fed.

if __name__ == '__main__':
    orch = Orchestrator()
    orch.build("yolov3-object-detection")
    orch.build("cntk-image-reco")

    yolo_arg = ["python3", "-m", "service.object_detection_service", "--grpc-port","8889"]
    yolo_cont = orch.create("yolov3-object-detection", yolo_arg, 8889)

    cntk_arg = ["/root/anaconda3/envs/cntk-py35/bin/python", "-m", "service.image_recon_service", "--grpc-port","8890"]
    cntk_cont = orch.create("cntk-image-reco", cntk_arg, 8890)

    orch.call("yolo", 8889)

    orch.delete(yolo_cont)
    orch.delete(cntk_cont)
