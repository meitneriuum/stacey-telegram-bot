from typing import Optional
from telegram import Update


class ExtendedUpdate(Update):
    __slots__ = ["_effective_text", "_message_type", "_update_type"]
    
    def __init__(self, update: Update) -> None:
        super().__init__(
            update.update_id, 
            update.message, 
            update.edited_message, 
            update.channel_post, 
            update.edited_channel_post, 
            update.inline_query,  
            update.chosen_inline_result,  
            update.callback_query,  
            update.shipping_query,  
            update.pre_checkout_query,  
            update.poll,  
            update.poll_answer,  
            update.my_chat_member,  
            update.chat_member,  
            update.chat_join_request,  
            **update.api_kwargs)
        self._effective_text: Optional[str] = None
        self._message_type: Optional[str] = None
        self._update_type: Optional[str] = None

    @property
    def effective_text(self) -> Optional[str]:
        
        if self._effective_text:
            return self._effective_text
        
        text: Optional[str] = None
        
        if self.effective_message:
            
            if self.callback_query:
                text = self.callback_query.data
                          
            elif self.effective_message.text:
                text = self.effective_message.text
                
            elif self.effective_message.caption:
                text = self.effective_message.caption
                

                
        self._effective_text = text
        return text
        
    @property
    def update_type(self) -> Optional[str]:
        
        if self._update_type:
            return self._update_type
        
        utype: Optional[str] = None
        
        if self.message:
            utype = self.MESSAGE
        
        elif self.edited_message:
            utype = self.EDITED_MESSAGE
        
        elif self.channel_post:
            utype = self.CHANNEL_POST
        
        elif self.edited_channel_post:
            utype = self.EDITED_CHANNEL_POST
        
        elif self.inline_query:
            utype = self.INLINE_QUERY
        
        elif self.chosen_inline_result:
            utype = self.CHOSEN_INLINE_RESULT
        
        elif self.callback_query:
            utype = self.CALLBACK_QUERY
        
        elif self.shipping_query:
            utype = self.SHIPPING_QUERY
        
        elif self.pre_checkout_query:
            utype = self.PRE_CHECKOUT_QUERY
        
        elif self.poll:
            utype = self.POLL
        
        elif self.poll_answer:
            utype = self.POLL_ANSWER
        
        elif self.my_chat_member:
            utype = self.MY_CHAT_MEMBER
        
        elif self.chat_member:
            utype = self.CHAT_MEMBER
        
        elif self.chat_join_request:
            utype = self.CHAT_JOIN_REQUEST
        
        self._update_type = utype
        return utype    
    
    @property
    def message_type(self) -> Optional[str]:
        
        if self._message_type:
            return self._message_type
        
        mtype: Optional[str] = None
        
        if self.effective_message.text:
            mtype = self.effective_message.text.__class__.__name__
        
        elif self.effective_message.audio:
            mtype = self.effective_message.audio.__class__.__name__
        
        elif self.effective_message.animation:
            mtype = self.effective_message.animation.__class__.__name__
        
        elif self.effective_message.document:
            mtype = self.effective_message.document.__class__.__name__
        
        elif self.effective_message.game:
            mtype = self.effective_message.game.__class__.__name__
        
        elif self.effective_message.photo:
            mtype = self.effective_message.photo[0].__class__.__name__
        
        elif self.effective_message.sticker:
            mtype = self.effective_message.sticker.__class__.__name__
        
        elif self.effective_message.story:
            mtype = self.effective_message.story.__class__.__name__
        
        elif self.effective_message.video:
            mtype = self.effective_message.video.__class__.__name__
        
        elif self.effective_message.voice:
            mtype = self.effective_message.voice.__class__.__name__
        
        elif self.effective_message.video_note:
            mtype = self.effective_message.video_note.__class__.__name__
        
        elif self.effective_message.caption:
            mtype = self.effective_message.caption.__class__.__name__
        
        elif self.effective_message.contact:
            mtype = self.effective_message.contact.__class__.__name__
        
        elif self.effective_message.location:
            mtype = self.effective_message.location.__class__.__name__
        
        elif self.effective_message.venue:
            mtype = self.effective_message.venue.__class__.__name__
        
        elif self.effective_message.successful_payment:
            mtype = self.effective_message.successful_payment.__class__.__name__
        
        elif self.effective_message.passport_data:
            mtype = self.effective_message.passport_data.__class__.__name__
        
        elif self.effective_message.poll:
            mtype = self.effective_message.poll.__class__.__name__
        
        elif self.effective_message.dice:
            mtype = self.effective_message.dice.__class__.__name__
        
        self._message_type = mtype
        return mtype