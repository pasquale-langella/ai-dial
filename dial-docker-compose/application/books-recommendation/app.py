import uvicorn
import json
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response
import file_utils
from openai import OpenAI

# ChatCompletion is an abstract class for applications and model adapters
class BooksRecommendationApplication(ChatCompletion):
    async def chat_completion(
        self, request: Request, response: Response
    ) -> None:
        
        # Get last message (the newest) from the history
        last_user_message = request.messages[-1]

        # Generate response with a single choice
        with response.create_single_choice() as choice:
            # Fill the content of the response with the last user's content
            llm_response = self.call_openai(last_user_message)
            choice.append_content(llm_response)

    def __compose_prompt__(self,user_prompt):
        print(user_prompt)
        with open('books.json', 'r') as file:
            books = json.load(file)
        i=0
        prompt = "Given book list:\n"
        for book in books:
            title = book["title"]
            desc = book["longDescription"][0:100]
            prompt+= "book #"+str(i)+" title="+title+" description="+desc+"\n"
            i+=1
        list_template =  "* book title: title \n book description: description \n"
        prompt+=("You are a recommendation system that must recommend a book in the given book list \n" +
                 "Steps to follow: \n"+
                 "1. Analyse user input. Identify the main goals. Plan your actions to achieve the user request \n"
                 "2. if the user asks to list the given books: then list the books following the template: " + list_template +
                 "3. if the user asks for a book recommendation: then recommend at most 3 books that meet the user preferences, to recommend the books use the following template: "+ list_template +
                 "Constraints: \n"+
                 "1. Only the books from the given list must be used \n"+
                 "2. You must use the same language as the user input. \n"+
                 "3. Your answers should be focused and follow all user instructions. \n" +
                 "4. book title and book description must be always on two different lines \n" +
                 "5. You should talk professionally like a salesperson in a shop \n"
                 "User Input: \n"+
                 user_prompt.content
                 )
        return prompt
    
    
    def call_openai(self,user_prompt):
        resp=""
        prompt=self.__compose_prompt__(user_prompt)
        print("--------------prompt-----------------------\n")
        print(prompt)
        client = OpenAI(api_key=file_utils.read_file("properties.sec")["open_api_key"])
        completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"user", "content":prompt}
        ])
        resp = completion.choices[0].message.content
        print(resp)
        return resp
    
# DIAL App extends FastAPI to provide an user-friendly interface for routing requests to your applications
app = DIALApp()
app.add_chat_completion("books-recommendation", BooksRecommendationApplication())

# Run builded app
if __name__ == "__main__":
    host="0.0.0.0"
    #host = "127.0.0.1" 
    uvicorn.run(app, port=5000, host=host)