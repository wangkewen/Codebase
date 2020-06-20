#include<bits/stdc++.h>
using namespace std;
struct Node{
    int val;
    Node* next;
};
bool _compare_and_swap(Node** des, Node* exp, Node* change){
    if(*des == exp){
        *des = change;
        return true;
    }else{
        return false;
    }
};
#define CAS _compare_and_swap
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
class RealLockFree{
public:
    atomic<Node*> top;
    RealLockFree(){
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
        Node* oldtop;
        do{
            oldtop = top;
        }while(!top.compare_exchange_weak(oldtop, oldtop->next));
        return oldtop->val;
    }
};
void shortest(){
    LockFreeStack lfs;
    for(int i = 0; i < 10; i++) lfs.push(i);
    while(lfs.top != nullptr) cout << lfs.pop() << endl;
}
void longtest(){
    RealLockFree rlf;
    vector<thread> threads;
    for(int i = 0; i < 10; i++){
        threads.push_back(thread(&RealLockFree::push, &rlf, i));
        //threads.push_back(thread(&RealLockFree::push, &rlf, i));
        //threads.push_back(thread(&RealLockFree::pop, &rlf));
    }
    for(auto & th : threads) th.join();
    while(rlf.top != nullptr) cout << rlf.pop() << endl;
}
int main(){
    //shortest();
    longtest();
}
