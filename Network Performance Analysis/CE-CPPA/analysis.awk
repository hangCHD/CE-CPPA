BEGIN {#模拟前，数据初始化
	highest_uid = 0; 
	v_num = 10;# 节点个数
	nodes = v_num + 4;
	id_MAX = 300000;# 初始化
	packet_sent[nodes] = 0;#每个节点对应一个发包计数器
	packet_loss[nodes] = 0;#每个节点对应一个丢包计数器
	packet_recvd[nodes] = 0;#每个节点对应一个收包计数器
	ratio_vd[nodes] = 0;#每个节点对应的验证比率
	sent_total = 0;# 总发包数
	recvd_total = 0;# 总收包数
	loss_total = 0;
	ratio_verify = 0;#总比率和
	pkt_Loss_ratio = 0;#丢包率
	packet_from[id_MAX] = 0;#每个分组对应一个发包节点
	start_time[id_MAX] = 0;# 每个分组对应的初始时间
	end_time[id_MAX] = 0;# 每个分组对应的结束时间
	repeat_num[id_MAX] = 0;# 每个分组重复接收次数
	packet_duration = 0.0;
	recvnum=0;
	sum=0.0;
	delay=0.0
	i=0;
	sign_time =  0.19796;
	verify_time = 0.09640;
	recvd_num_rsu = 0;
	run_time = 100;#总运行时间
	
	n_verify = int(run_time/verify_time);
}

{

	event = $1;
	time = $2;
	node = $3;
    	len = length(node);
    	node_id = substr(node,2,len-2);
	trace_type = $4;
	flag = $5;
	uid = $6;#分组uid
	pkt_type = $7;
	pkt_size = $8
		
	if(event=="s" && trace_type=="AGT" && pkt_type=="PBC"){
		packet_from[uid] = node_id;
		start_time[uid]=time;
        #每个分组发送包的时间点
        }

	if((event=="r") && (trace_type=="AGT") && (pkt_type=="PBC"))
	{
		end_time[uid]+=time;
	        #每个分组接收到包的时间点
		recvd_num_rsu += 1;
		repeat_num[uid] += 1;
	}
	if(highest_uid < uid)
		highest_uid = uid;
	
}

{
        #$变量分别按照序号对应tr文件中的字段
	event = $1;#第一个字段：事件
	time = $2;
	node = $3;
	len = length(node);
	node_id = substr(node,2,len-2);	
	uid = $6;#分组uid
	#node_id = substr($3,2,1);#第三个字段从第二位开始的一个子字段，即节点id
	layer = $4;
	flag = $5;
	pkt_type = $7;
	if(pkt_type == "PBC" && event == "s" && layer == "AGT"){
		packet_sent[node_id] = packet_sent[node_id] + 1;
	}
	if(pkt_type == "PBC" && event == "r" && layer == "AGT"){
		packet_recvd[node_id] = packet_recvd[node_id] + 1;
        	#计算接受到的包的个数
	}
	if(pkt_type == "PBC" && event == "D" && flag == "---"){
		packet_loss[node_id] = packet_loss[node_id] + 1;
	}
}

END {
	for(i = 0; i <= highest_uid; i++)
	{
		#printf("Packets %d  repeat received times:       %d\n",i,repeat_num[i])> "repeat_num.txt";
		start = start_time[i];
		end = end_time[i];
		#packet_duration = end-start*repeat_num[i];#每组包从发送到被接收所用时间
		#packet_duration = end - start;
		if(start<=end){
			packet_duration = end-start*repeat_num[i];#每组包从发送到被接收所用时间
			sum += packet_duration;#所有时间
			recvnum++;#接收次数	
			printf("Packets %d  delay    :      %.6f\n", i, packet_duration) > "delay.txt";
			printf("Packets %d  sent time   :       %.6f\n",i,start)> "start_time.txt";
	                printf("Packets  %d Received time       %.6f\n",i,end)> "end_time.txt";	
			printf("Packets %d  repeat received times:       %d\n",i,repeat_num[i])> "repeat_num.txt";
		}
		
	} 
	delay=sum/recvd_num_rsu + sign_time;#平均时延
	delay+=verify_time;
	printf("Average End to End Delay 	:	%.9f s\n", delay);
	


	for(i=0;i<nodes;i++) {
        #计算每个节点发出的包和丢失的包的个数
        	sent_total = sent_total + packet_sent[i];
        	loss_total = loss_total + packet_loss[i];
                printf("%d %d \n",i, packet_sent[i]) > "pktsent.txt";
                printf("%d %d \n",i, packet_loss[i]) > "pktloss.txt";
                
	}
	#计算因验证不及时导致丢失的包的个数
	for(i=0; i<nodes;i++)
	{	
		printf("%d %d \n",i, packet_recvd[i]) > "pktrecvd.txt";
		if(n_verify < packet_recvd[i])
		{
			loss_total = loss_total + packet_recvd[i] - n_verify;
		}		
	}
	pkt_Loss_ratio = loss_total/sent_total;
	printf("Packet Loss Ratio 		:	%.6f\n\n",pkt_Loss_ratio);
}
