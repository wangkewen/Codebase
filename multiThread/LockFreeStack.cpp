#include<bits/stdc++.h>
using namespace std;

struct Node{
    int val;
    Node* next;
    //Node(int x) : val(x) {}
};

bool __compare_and_swap(Node** des, Node* exp, Node* newvalue){
    if(*des == exp){
        *des = newvalue;
        return true;
    }else{
        return false;
    }
}
#define CAS __compare_and_swap
class LockFreeStack{
public:
    Node* top;
    LockFreeStack(){
        top = nullptr;
    }
    void push(int x){
        Node* newtop = new Node{x, nullptr};
        do{
            newtop->next = top;
        }while(!CAS(&top, newtop->next, newtop));
        return;
    }
    int pop(){
        if(top == nullptr) return -1;
        Node* oldtop;
        do{
           oldtop = top;
        }while(!CAS(&top, oldtop, oldtop->next));
        return oldtop->val;
    }
};
class realLockFree{
public:
    atomic<Node*> top;
    realLockFree(){
        top = nullptr;
    }
    void push(int x){
        Node* newtop = new Node{x, nullptr};
        do{
            newtop->next = top;
        }while(!top.compare_exchange_weak(newtop->next, newtop));
        return;
    }
    int pop(){
        if(top == nullptr) return -1;
        Node* old;
        do{
            old = top;
        }while(!top.compare_exchange_weak(old, old->next));
        return old->val;
    }
};
void tt(int x){
    cout << x << endl;
}
void shortest(){
    int n = 10;
    vector<thread> threads;
    for(int i = 0; i < n; i++){
        threads.push_back(thread(tt, i));
    }
    for(auto& th : threads) th.join();
}
void longtest(){
    int n = 10;
    vector<thread> threads;
    realLockFree rlf;
    for(int i = 0; i < n; i++){
        threads.push_back(thread(&realLockFree::push, &rlf, i));
        threads.push_back(thread(&realLockFree::push, &rlf, i));
        threads.push_back(thread(&realLockFree::pop, &rlf));
    }
    for(auto& th : threads) th.join();
    while(rlf.top != nullptr){
        cout << rlf.pop() << endl;
    }
}
int main(){
    longtest();
    LockFreeStack lfs;
    lfs.push(10);
    lfs.push(11);
    //cout << lfs.pop() << endl;
}
