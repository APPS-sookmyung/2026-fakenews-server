package com.fakenews.server.domain.post.controller;

import com.fakenews.server.domain.post.dto.PostRegisterReqDto;
import com.fakenews.server.domain.post.dto.PostReadResDto;
import com.fakenews.server.domain.post.dto.PostRegisterResDto;
import com.fakenews.server.domain.post.service.PostService;
import lombok.RequiredArgsConstructor;

import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
public class PostController {

    private final PostService postService;

    @PostMapping("/post/register")
    public PostRegisterResDto register(@RequestBody PostRegisterReqDto postRegisterReqDto){

        return postService.register(postRegisterReqDto);
    }

    @GetMapping("/post/{postId}")
    public PostReadResDto read(@PathVariable Long postId){
        return postService.read(postId);
    }

}
