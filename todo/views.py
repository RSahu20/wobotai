from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TaskList, Task, ListAccess
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
   
# Add list 
class ListAdd(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # Checking if 'name' parameter is provided and not empty
        if request.data.get('name', None) and request.data.get('name') != '':
            # Getting request data
            name = request.data.get('name')
            description = request.data.get('description', '')

            # Writing to database
            try:
                # Creating new TaskList object and saving it to the database
                new_list = TaskList(name=name, description=description)
                new_list.save()
                # Creating ListAccess object for the user with 'owner' role
                new_list_access = ListAccess(user=request.user, list=new_list, role='owner')
                new_list_access.save()

                # Responding back with success message and details of the newly created list
                resp_dict = {
                    'status': 'success',
                    'message': 'List created successfully',
                    'data': {'id': new_list.id, 'name': new_list.name, 'description': new_list.description}
                }
                resp = Response(resp_dict, status=status.HTTP_201_CREATED)
            except ValueError as val_err:
                # Responding back with error message if there's an issue with database operations
                resp_dict = {
                    'status': 'failed',
                    'message': 'Something went wrong while writing to database, {0}'.format(val_err),
                    'data': {}
                }
                resp = Response(resp_dict, status=status.HTTP_400_BAD_REQUEST)
            except Exception as er:
                # Responding back with error message if there's an unexpected error
                resp_dict = {
                    'status': 'failed',
                    'message': 'Something unexpected happened!, {0}'.format(er),
                    'data': {}
                }
                resp = Response(resp_dict, status=status.HTTP_400_BAD_REQUEST)

        else:
            # Responding back with error message if 'name' parameter is missing or empty
            resp_dict = {
                'status': 'failed',
                'message': 'List name is required but not provided',
                'data': {}
            }
            resp = Response(resp_dict, status=status.HTTP_400_BAD_REQUEST)

        return resp


class ListFetch(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        resp_dict = {
            'status': '',
            'message': '',
            'data': None
        }

        try:
            # Fetching the IDs of lists accessible to the user
            list_ids = ListAccess.objects.values_list('list').filter(user=request.user)
            # Fetching details of the lists
            lists = TaskList.objects.filter(id__in=list_ids).values()
            resp_dict['status'] = 'Success'
            resp_dict['message'] = 'Retrieved the list of todo lists'
            resp_dict['data'] = lists

        except Exception as e:
            # Handling exceptions and returning error response
            print(e)
            resp_dict['status'] = 'Failed'
            resp_dict['message'] = 'Something went wrong while fetching data. Error: '+e.__str__()
            resp_dict['data'] = None

        return Response(resp_dict)


from datetime import datetime

class TaskAdd(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        resp_dict = {
            'status': None,
            'message': None,
            'data': None
        }

        # Extracting request parameters
        req_list_id = request.data.get("list_id")
        req_task_name = request.data.get("name")
        req_task_desc = request.data.get('description', '')
        req_task_date = request.data.get('date', None)
        req_task_priority = request.data.get('priority', None)

        if req_list_id and TaskList.objects.filter(id=req_list_id).exists() and \
                req_task_name and req_task_name != '':
            try:
                # Fetching TaskList object
                task_list = TaskList.objects.get(id=req_list_id)

                # Checking user's permission to edit the list
                user_perm = ListAccess.objects.filter(user=request.user, list=task_list)

                if user_perm.count() != 1 or user_perm.first().role != 'owner':
                    raise PermissionError("You do not have permission to edit this list")

                # Creating the task with additional fields
                new_task = Task(
                    name=req_task_name,
                    list=task_list,
                    description=req_task_desc,
                    date=req_task_date,
                    priority=req_task_priority
                )
                new_task.save()

                # Responding back with success message and details of the newly created task
                resp_dict['status'] = "success"
                resp_dict['message'] = "Task creation successful"
                resp_dict['data'] = {
                    "name": new_task.name,
                    "description": new_task.description,
                    "done": new_task.done,
                    "list_id": new_task.list.id,
                    "date": new_task.date,
                    "priority": new_task.priority
                }
                resp = Response(resp_dict)
                resp.status_code = status.HTTP_200_OK

            except PermissionError as pe:
                # Handling permission-related error and returning appropriate response
                resp_dict['status'] = "failed"
                resp_dict['message'] = pe.__str__()
                resp_dict['data'] = None
                resp = Response(resp_dict, status=status.HTTP_403_FORBIDDEN)
            except Exception as e:
                # Handling other errors and returning appropriate response
                resp_dict['status'] = "failed"
                resp_dict['message'] = "Something went wrong, Error: "+e.__str__()
                resp_dict['data'] = None
                resp = Response(resp_dict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            # Responding back with error message if required parameters are missing or invalid
            resp_dict['status'] = "failed"
            resp_dict['message'] = "Invalid name or list_id passed"
            resp_dict['data'] = None
            resp = Response(resp_dict, status=status.HTTP_400_BAD_REQUEST)

        return resp



class TaskFetch(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        resp_dict = {
            'status': None,
            'message': None,
            'data': None
        }

        try:
            list_id = request.query_params.get("list_id", None)

            # checking if the list id is provided
            if list_id is None or list_id == '':
                raise ValueError("Invalid list_id")

            # fetching list object
            try:
                task_list_obj = TaskList.objects.get(id=list_id)
            except ObjectDoesNotExist:
                raise ValueError("Invalid list_id")

            # checking if the user has permission on the given list
            try:
                list_perm_qs = ListAccess.objects.get(user=request.user, list=task_list_obj)
            except ObjectDoesNotExist:
                raise PermissionError("You do not have permission to access this list")

            # fetching tasks
            tasks = Task.objects.filter(list=task_list_obj).values()

            resp_dict['status'] = "success"
            resp_dict['message'] = "Fetched tasks successfully"
            resp_dict['data'] = tasks
            resp = Response(resp_dict)
            resp.status_code = status.HTTP_200_OK

        except PermissionError as pe:
            resp_dict['status'] = "failed"
            resp_dict['message'] = pe.__str__()
            resp_dict['data'] = None
            resp = Response(resp_dict, status=status.HTTP_403_FORBIDDEN)
        except ValueError as ve:
            resp_dict['status'] = "failed"
            resp_dict['message'] = ve.__str__()
            resp_dict['data'] = None
            resp = Response(resp_dict, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            resp_dict['status'] = "failed"
            resp_dict['message'] = "Something went wrong, Error: " + e.__str__()
            resp_dict['data'] = None
            resp = Response(resp_dict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return resp


class TaskStatusSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        resp_dict = {
            'status': None,
            'message': None,
            'data': None
        }

        try:
            task_id = request.data.get("task_id")
            new_status = request.data.get("status")

            # checking if the list id is provided
            if task_id is None or task_id == '':
                raise ValueError("Invalid task_id")

            # checking if new_status is valid boolean
            if new_status is None or new_status.lower() not in ['true', 'false']:
                raise ValueError("Invalid status passed")

            new_status = True if new_status.lower() == 'true' else False

            # fetching task object
            try:
                task_obj = Task.objects.get(id=task_id)
            except ObjectDoesNotExist:
                raise ValueError("Invalid task_id")

            # Checking if the user has permission on this list to which this task belongs
            try:
                user_perm = ListAccess.objects.get(user=request.user, list=task_obj.list)
                if user_perm.role != 'owner':
                    raise PermissionError("You do not have permission to edit this task")
            except ObjectDoesNotExist:
                raise PermissionError("You do not have permission to edit this task")

            task_obj.done = new_status

            task_obj.save()

            resp_dict['status'] = "success"
            resp_dict['message'] = "Updated task status successfully"
            resp_dict['data'] = {"id": task_obj.id, "name": task_obj.name, "list_id": task_obj.list.id,
                                 "status": task_obj.done, "description": task_obj.description}
            resp = Response(resp_dict)
            resp.status_code = 200

        except PermissionError as pe:
            resp_dict['status'] = "failed"
            resp_dict['message'] = pe.__str__()
            resp_dict['data'] = None
            resp = Response(resp_dict)
            resp.status_code = 403

        except ValueError as ve:
            resp_dict['status'] = "failed"
            resp_dict['message'] = ve.__str__()
            resp_dict['data'] = None
            resp = Response(resp_dict)
            resp.status_code = 400
        except Exception as e:
            resp_dict['status'] = "failed"
            resp_dict['message'] = "Something went wrong, Error: " + e.__str__()
            resp_dict['data'] = None
            resp = Response(resp_dict)
            resp.status_code = 500

        return resp



class ListDelete(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, list_id):
        try:
            list_obj = TaskList.objects.get(id=list_id)
        except TaskList.DoesNotExist:
            return Response({"message": "List does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        user_perm = ListAccess.objects.filter(user=request.user, list=list_obj)

        if user_perm.count() != 1 or user_perm.first().role != 'owner':
            return Response({"message": "You do not have permission to delete this list"}, status=status.HTTP_403_FORBIDDEN)

        list_obj.delete()
        return Response({"message": "List deleted successfully"}, status=status.HTTP_200_OK)


class TaskDelete(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, task_id):
        try:
            task_obj = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"message": "Task does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        user_perm = ListAccess.objects.filter(user=request.user, list=task_obj.list)

        if user_perm.count() != 1 or user_perm.first().role != 'owner':
            return Response({"message": "You do not have permission to delete this task"}, status=status.HTTP_403_FORBIDDEN)

        task_obj.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_200_OK)


# from django.utils import timezone
# from datetime import timedelta

# class LeastTimeLeftTasks(APIView):
#     permission_classes = (IsAuthenticated,)

#     def get(self, request):
#         resp_dict = {
#             'status': None,
#             'message': None,
#             'data': None
#         }

#         try:
#             # Get current date
#             current_date = timezone.now().date()

#             # Calculate the deadline date 7 days from now
#             deadline_date = current_date + timedelta(days=7)

#             # Fetch tasks that have their deadline within the next 7 days
#             tasks = Task.objects.filter(list__access__user=request.user, date__range=[current_date, deadline_date]).order_by('date').values()

#             resp_dict['status'] = "success"
#             resp_dict['message'] = "Fetched tasks with the least time left successfully"
#             resp_dict['data'] = tasks
#             resp = Response(resp_dict)
#             resp.status_code = 200

#         except Exception as e:
#             resp_dict['status'] = "failed"
#             resp_dict['message'] = "Something went wrong, Error: " + e.__str__()
#             resp_dict['data'] = None
#             resp = Response(resp_dict)
#             resp.status_code = 500

#         return resp
