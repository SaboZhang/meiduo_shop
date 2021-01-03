/*
 * @Author: 张涛
 * @Date: 2020-11-22 16:37:36
 * @LastEditTime: 2020-11-26 22:54:47
 * @LastEditors: 张涛
 * @Description: 注册js文件
 * @FilePath: /meiduo_shop/static/js/register.js
 * @世界上最遥远的距离不是生与死，而是你亲手制造的BUG就在你眼前，你却怎么都找不到她
 */
let vm = new Vue({
    el:'#app',
    delimiters: ['[[',']]'],
    data: {
        username: '',
        password: '',
        password2: '',
        mobile: '',
        allow: '',
        image_code_url:'',
        uuid:'',
        image_code:'',
        sms_code:'',

        error_name: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow:false,
        error_code:false,
        error_sms_code:false,
        sending_flag:false,

        error_name_message: '',
        error_mobile_message: '',
        error_code_message:'',
        sms_code_message:'',
        sms_code_tip:'获取短信验证码',
    },
    mounted(){
        this.generate_image_code()
    },
    methods: {
        check_sms_code(){
            if(this.sms_code.length != 6){
                this.sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        send_sms_code() {
             // 避免重复点击
            if (this.sending_flag == true) {
                return;
            }
            this.sending_flag = true;

            // 校验参数
            this.check_mobile();
            this.check_verify_code();
            if (this.error_mobile == true || this.check_verify_code == true) {
                this.sending_flag = false;
                return;
            }
            let url = '/verify/sms_codes/' + this.mobile + '/?image_code=' + this.image_code+'&uuid='+ this.uuid;

            axios.get(url, {
                responseType: 'json'
            })
                .then(response =>{
                    if (response.data.code == '0'){
                        //倒计时60秒
                        let num = 60;
                        let t = setInterval(() =>{
                            if (num == 1){
                                clearInterval(t);
                                this.sms_code_tip = '获取短信验证码';
                                this.generate_image_code();
                                this.sending_flag = false;
                            }else {
                                num -= 1;
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000)

                    }else {
                        if (response.data.code == '4001'){
                            this.error_code_message = response.data.errmsg;
                            this.error_code = true;
                            this.generate_image_code();
                        }else {
                            this.sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                        }
                        this.sending_flag = false;
                    }
                })
                .catch(error =>{
                    this.sending_flag = false;
                    console.log(error.response)
                })
        },
        //生成验证码
        generate_image_code(){
            //生成UUID
            this.uuid = generateUUID();
            this.image_code_url = '/verify/image_code/' + this.uuid + '/';
        },
        //校验验证码
        check_verify_code(){
            if (this.image_code.length != 4){
                this.error_code_message = '请填写验证码';
                this.error_code = true;
            }else {
                this.error_code = false;
            }
        },
        //用户名验证
        check_username(){
            let re = /^[a-zA-Z0-9_-]{4,16}$/;
            if(re.test(this.username)){
                this.error_name = false;
            }else{
                this.error_name_message = '请输入4-16字符的用户名';
                this.error_name = true;
            }
            //判断用户名是否重复
            if (this.error_name == false){
                let url = '/user/usernames/' + this.username + '/count/'
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.count >= 1){
                            this.error_name_message = '用户名已存在';
                            this.error_name = true;
                        }else {
                            this.error_name = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response)
                    })
            }
        },
        //密码验证
        check_password(){
            let re = /^[0-9A-Za-z]{8,20}$/;
            if(re.test(this.password)){
                this.error_password = false;
            }else{
                this.error_password = true;
            }
        },
        //密码二次校验
        check_password2(){
            if(this.password != this.password2){
                this.error_password2 = true;
            }else{
                this.error_password2 = false;
            }
        },
        //手机号验证
        check_mobile(){
            let re = /^(?:(?:\+|00)86)?1(?:(?:3[\d])|(?:4[5-7|9])|(?:5[0-3|5-9])|(?:6[5-7])|(?:7[0-8])|(?:8[\d])|(?:9[1|8|9]))\d{8}$/;
            if(re.test(this.mobile)){
                this.error_mobile = false;
            }else{
                this.error_mobile_message = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }
            if (this.error_mobile == false){
                let url = '/user/mobiles/' + this.mobile + '/count/'
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response =>{
                        if (response.data.count >= 1){
                            this.error_mobile_message = '手机号已存在';
                            this.error_mobile = true;
                        }else {
                            this.error_mobile = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response)
                    })
            }

        },
        //是否同意用户注册协议
        check_allow(){
            if(!this.allow){
                this.error_allow = true;
            }else{
                this.error_allow = false;
            }
        },
        //监听表单提交事件
        on_submit(){
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_sms_code();
            this.check_allow();

            //判断是否进行提交
            if(this.error_name == true || this.error_password == true || this.error_password2 == true 
                || this.error_mobile == true || this.error_sms_code == true || this.error_allow == true){
                    //禁用表单提交按钮
                window.event.preventDefault()
            }
        },
    }
});
    

