$(document).ready(function(){

	let base_url=window.location.origin
	let url_href=window.location.href
	var lastPart =url_href.split("/")
	let pk=lastPart.pop()
	if (pk===""){
		pk=lastPart.pop()
	
	}
	
	
   let icon_like=` <svg style="
   margin-top: 10px;
           display: inline-block;
           width: 20px;
           height: 20px;
         color: #c49b63;
           
                 " xmlns="http://www.w3.org/2000/svg" fill="#c49b63" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
   </svg>`
    let icon_unlike=`<svg style="
    margin-top: 10px;
    display: inline-block;
    width: 20px;
    height: 20px;
    color: #c49b63;
    
                " xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                </svg>`

    let like_count=document.getElementById("like_count")
    let area=document.getElementById("like_area")
    let like_statuss;
    if (area){
        area.addEventListener("click",function(e){
            e.preventDefault()

        //    let like_s=area.dataset
       
          if(like_statuss) {
            $.ajax({
            url:`/delet_like/${pk}/`,

            type: 'GET',
            dataType: 'json', // added data type
            cache: false,
            
            processData: false,
            contentType: false,
            success: function(res) {
                console.log(res);
               
                // area.setAtribute("like","unlike");
                area.innerHTML=icon_unlike;
                like_count.innerHTML=res.like_count
                like_statuss=false;
            },
            error:function(res){

                console.log("erroe",res,res.responseText);
                
                
            }
            })//end ajax
          }//end if
          else {
            $.ajax({
            url:`/create_like/${pk}/`,

            type: 'GET',
            dataType: 'json', // added data type
            cache: false,
            
            processData: false,
            contentType: false,
            success: function(res) {
                console.log(res);
               
                // area.setAtribute("like","like");
                area.innerHTML=icon_like;
                like_count.innerHTML=res.like_count;
                like_statuss=true;

            },
            error:function(res){

                console.log("erroe",res,res.responseText);
               
                
            }
            })//end ajax
          }//end else

        })

    }//end if area
    $.ajax({
        url:`/json_check_like/${pk}/`,

        type: 'GET',
        dataType: 'json', // added data type
        cache: false,
        
        processData: false,
        contentType: false,
        
        success: function(res) {
            console.log(res);
           
            
            if(res.liked_status){
                // area.setAtribute("like","like");
            area.innerHTML=icon_like;
            like_statuss=true;
            }
            else{
                // area.setAtribute("like","unlike");
                 area.innerHTML=icon_unlike;
                 like_statuss=false;
            }
            console.log(like_statuss)
            like_count.innerHTML=res.like_count
            

        },
        error:function(res){

            console.log("erroe",res,res.responseText);
            
            
        }
        })//end ajax

   
})